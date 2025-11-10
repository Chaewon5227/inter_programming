"""Core level views for the combined planner + budget experience."""

from __future__ import annotations

import calendar
from datetime import date, datetime, time, timedelta

from django.db.models import Q, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from finance.models import Account, Category, Transaction
from tasks.models import Task


def _parse_selected_date(request):
    """사용자가 선택한 날짜 문자열을 안전하게 date 객체로 변환한다."""

    # 잘못된 형식이 들어와도 오늘 날짜로 폴백하여 페이지를 안전하게 보여준다.
    date_param = request.GET.get('date')
    if date_param:
        try:
            return datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError:
            pass
    return timezone.localdate()


def _process_planner_forms(request, selected_date, success_base_path):
    """하루 단위 플래너에서 사용하는 폼을 공통으로 처리한다."""

    form_errors: list[str] = []

    if request.method != 'POST':
        # GET 요청이라면 바로 에러 없이 반환한다.
        return None, form_errors

    form_type = request.POST.get('form_type')

    if form_type == 'schedule_entry':
        # 일정 기본 정보
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not title:
            form_errors.append('일정 제목을 입력해주세요.')

        if not start_time:
            form_errors.append('시작 시간을 입력해주세요.')

        if not form_errors:
            start_at = _combine_with_date(selected_date, start_time, time(hour=9))
            # 종료 시간은 비어 있다면 1시간 뒤로 잡는다.
            if end_time:
                due_at = _combine_with_date(selected_date, end_time, time(hour=10))
            else:
                due_at = start_at + timedelta(hours=1)

            # 가계부 입력 값에 대한 검증을 먼저 수행한다.
            amount = request.POST.get('amount')
            account_id = request.POST.get('account') or None
            category_id = request.POST.get('category') or None
            memo = request.POST.get('memo', '').strip()
            transaction_kwargs = None

            if amount:
                if not (account_id and category_id):
                    form_errors.append('금액을 입력했다면 계정과 분류도 선택해주세요.')
                else:
                    transaction_kwargs = dict(
                        owner=request.user,
                        account_id=account_id,
                        category_id=category_id,
                        amount=amount,
                        memo=memo,
                        occurred_at=start_at,
                    )

            if not form_errors:
                # 일정 레코드를 생성한다.
                task = Task.objects.create(
                    owner=request.user,
                    title=title,
                    description=description,
                    start_at=start_at,
                    due_at=due_at,
                    is_all_day=False,
                )

                if transaction_kwargs:
                    Transaction.objects.create(task=task, **transaction_kwargs)

                return redirect(f"{success_base_path}?date={selected_date.isoformat()}"), form_errors

    elif form_type == 'loose_transaction':
        # 일정과 무관한 단독 지출 입력 처리
        account_id = request.POST.get('account') or None
        category_id = request.POST.get('category') or None
        amount = request.POST.get('amount')
        memo = request.POST.get('memo', '').strip()
        occurred_time = request.POST.get('occurred_time')

        if not occurred_time:
            form_errors.append('소비 시간을 입력해주세요.')

        if not (account_id and category_id and amount):
            form_errors.append('계정, 분류, 금액을 모두 입력해주세요.')

        if not form_errors:
            occurred_at = _combine_with_date(selected_date, occurred_time, time(hour=12))
            Transaction.objects.create(
                owner=request.user,
                account_id=account_id,
                category_id=category_id,
                amount=amount,
                memo=memo,
                occurred_at=occurred_at,
            )
            return redirect(f"{success_base_path}?date={selected_date.isoformat()}"), form_errors

    return None, form_errors


def _build_calendar_data(selected_date, user):
    """월간 달력 표시에 필요한 부가 정보를 계산한다."""

    first_of_month = selected_date.replace(day=1)
    # 32일을 더하면 항상 다음 달로 이동한다는 점을 활용한다.
    next_month_base = first_of_month + timedelta(days=32)
    prev_month_base = first_of_month - timedelta(days=1)
    next_month = next_month_base.replace(day=1)
    prev_month = prev_month_base.replace(day=1)

    cal = calendar.Calendar(firstweekday=6)  # 6=일요일을 주의 시작으로 지정한다.
    today = timezone.localdate()

    month_range_end_day = calendar.monthrange(selected_date.year, selected_date.month)[1]
    month_start = first_of_month
    month_end = first_of_month.replace(day=month_range_end_day)

    monthly_tasks = (
        Task.objects.filter(owner=user)
        .filter(
            Q(start_at__date__range=(month_start, month_end))
            | Q(due_at__date__range=(month_start, month_end))
        )
        .only('id', 'start_at', 'due_at')
    )

    tasks_by_day: dict[date, set[int]] = {}
    for task in monthly_tasks:
        # 시작일과 마감일이 같은 날짜일 수 있으므로 집합으로 관리한다.
        for dt_field in (task.start_at, task.due_at):
            if not dt_field:
                continue
            localized_date = timezone.localtime(dt_field).date()
            if month_start <= localized_date <= month_end:
                tasks_by_day.setdefault(localized_date, set()).add(task.id)

    calendar_weeks = []
    for week in cal.monthdatescalendar(selected_date.year, selected_date.month):
        week_cells = []
        for day in week:
            week_cells.append(
                {
                    'date': day,
                    'in_month': day.month == selected_date.month,
                    'is_today': day == today,
                    'is_selected': day == selected_date,
                    'task_count': len(tasks_by_day.get(day, set())),
                }
            )
        calendar_weeks.append(week_cells)

    return {
        'calendar_weeks': calendar_weeks,
        'calendar_weekdays': ['일', '월', '화', '수', '목', '금', '토'],
        'prev_month': prev_month,
        'next_month': next_month,
    }


def _build_planner_context(request, selected_date, form_errors, include_calendar=True):
    """대시보드와 상세 페이지에 공통으로 전달할 컨텍스트를 생성한다."""

    # 일정과 거래를 조회할 범위를 하루 단위로 계산한다.
    day_start = _combine_with_date(selected_date, "00:00", time.min)
    day_end = _combine_with_date(selected_date, "23:59", time.max)

    # 일정은 시작일 또는 마감일이 해당 날짜에 걸쳐 있는 것만 모은다.
    tasks = (
        Task.objects.filter(owner=request.user)
        .filter(
            Q(start_at__date=selected_date)
            | Q(due_at__date=selected_date)
        )
        .prefetch_related('linked_transactions__category', 'linked_transactions__account')
        .order_by('start_at', 'due_at', 'title')
    )

    # 선택한 날짜에 발생한 모든 거래를 가져온다.
    transactions = (
        Transaction.objects.filter(owner=request.user, occurred_at__range=(day_start, day_end))
        .select_related('account', 'category', 'task')
        .order_by('occurred_at')
    )

    # 타임라인 UI에서 시간을 가진 일정과 그렇지 않은 일정을 분리한다.
    timed_tasks: list[dict[str, object]] = []
    untimed_tasks: list[dict[str, object]] = []

    for task in tasks:
        # 템플릿에서 반복적으로 지역 시간을 계산하지 않도록 미리 변환해 둔다.
        start_local = timezone.localtime(task.start_at) if task.start_at else None
        end_local = timezone.localtime(task.due_at) if task.due_at else None
        linked_transactions = list(task.linked_transactions.all())

        task_payload = {
            'task': task,
            'start_local': start_local,
            'end_local': end_local,
            'transactions': linked_transactions,
        }

        if start_local or end_local:
            timed_tasks.append(task_payload)
        else:
            untimed_tasks.append(task_payload)

    # 일정에 연결되지 않은 지출은 별도의 섹션에 보여준다.
    loose_transactions = [
        tx for tx in transactions if tx.task_id is None
    ]

    # 수입/지출 합계를 미리 계산해 카드에 보여준다.
    daily_totals = {
        row['category__kind']: row['total']
        for row in transactions.values('category__kind').annotate(total=Sum('amount'))
    }

    accounts = Account.objects.filter(owner=request.user)
    expense_categories = Category.objects.filter(owner=request.user, kind='expense')

    context = {
        'selected_date': selected_date,
        'tasks': tasks,
        'transactions': transactions,
        'timed_tasks': timed_tasks,
        'untimed_tasks': untimed_tasks,
        'loose_transactions': loose_transactions,
        'daily_totals': daily_totals,
        'accounts': accounts,
        'categories': expense_categories,
        'form_errors': form_errors,
    }

    if include_calendar:
        # 대시보드에서만 월간 달력 데이터가 필요하다.
        context.update(_build_calendar_data(selected_date, request.user))

    return context


def _combine_with_date(selected_date, time_str, fallback):
    """Helper to merge a date with a HH:MM string while keeping timezone awareness."""

    # 문자열이 들어오면 시각을 파싱하고, 없으면 기본값을 사용한다.
    if time_str:
        parsed_time = datetime.strptime(time_str, "%H:%M").time()
    else:
        parsed_time = fallback

    naive_datetime = datetime.combine(selected_date, parsed_time)
    # settings.USE_TZ=True 환경에서도 안전하게 시간대를 적용한다.
    if timezone.is_naive(naive_datetime):
        return timezone.make_aware(naive_datetime, timezone.get_current_timezone())
    return naive_datetime


def home_redirect(request):
    """Root URL 접근 시 플래너로 자연스럽게 연결한다."""

    # 메인 페이지를 찾는 사용자를 바로 통합 플래너로 안내한다.
    return redirect('planner_dashboard')


def planner_dashboard(request):
    """일정과 가계부를 하루 단위로 함께 살펴볼 수 있는 대시보드."""

    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.path)

    selected_date = _parse_selected_date(request)

    redirect_response, form_errors = _process_planner_forms(
        request,
        selected_date,
        success_base_path='/planner/'
    )
    if redirect_response:
        return redirect_response

    context = _build_planner_context(
        request,
        selected_date,
        form_errors,
        include_calendar=True,
    )
    return render(request, 'planner/dashboard.html', context)


def planner_day_detail(request):
    """더보기 링크로 진입하는 하루 전용 상세 페이지."""

    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.path)

    selected_date = _parse_selected_date(request)

    redirect_response, form_errors = _process_planner_forms(
        request,
        selected_date,
        success_base_path='/planner/day/'
    )
    if redirect_response:
        return redirect_response

    context = _build_planner_context(
        request,
        selected_date,
        form_errors,
        include_calendar=False,
    )
    return render(request, 'planner/day_detail.html', context)
