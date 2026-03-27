from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from .models import db, User, Group, Student, Homework, Attendance, StudentHomework
from .forms import LoginForm, GroupForm, StudentForm, HomeworkForm, HWSubmitForm
from .utils import render_markdown
from datetime import date, datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    return redirect(url_for('.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)  # remember по желанию
            next_page = request.args.get('next')
            # Безопасная проверка next
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

@bp.route('/groups')
@login_required
def groups():
    groups = Group.query.all()
    return render_template('groups.html', groups=groups)

@bp.route('/group/add', methods=['GET', 'POST'])
@login_required
def group_add():
    if current_user.role != 'teacher' and current_user.role != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('.groups'))
    form = GroupForm()
    if form.validate_on_submit():
        g = Group(name=form.name.data)
        db.session.add(g)
        db.session.commit()
        flash('Группа добавлена', 'success')
        return redirect(url_for('.groups'))
    return render_template('group_add.html', form=form)

@bp.route('/group/<int:group_id>/delete')
@login_required
def group_delete(group_id):
    if current_user.role != 'teacher' and current_user.role != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('.groups'))
    g = Group.query.get_or_404(group_id)
    db.session.delete(g)
    db.session.commit()
    flash('Группа удалена', 'success')
    return redirect(url_for('.groups'))

@bp.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@bp.route('/student/add', methods=['GET', 'POST'])
@login_required
def student_add():
    if current_user.role != 'teacher' and current_user.role != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('.students'))
    form = StudentForm()
    form.group_id.choices = [(g.id, g.name) for g in Group.query.all()]
    if form.validate_on_submit():
        s = Student(name=form.name.data, group_id=form.group_id.data)
        db.session.add(s)
        db.session.commit()
        flash('Студент добавлен', 'success')
        return redirect(url_for('.students'))
    return render_template('student_add.html', form=form)

@bp.route('/student/<int:student_id>/delete')
@login_required
def student_delete(student_id):
    if current_user.role != 'teacher' and current_user.role != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('.students'))
    s = Student.query.get_or_404(student_id)
    db.session.delete(s)
    db.session.commit()
    flash('Студент удалён', 'success')
    return redirect(url_for('.students'))

@bp.route('/attendance/<int:group_id>')
@login_required
def attendance(group_id):
    group = Group.query.get_or_404(group_id)
    today = date.today()
    students = group.students.all()
    if request.args.get('date'):
        att_date = datetime.strptime(request.args['date'], '%Y-%m-%d').date()
    else:
        att_date = today
    records = {a.student_id: a for a in Attendance.query.filter_by(group_id=group.id, date=att_date).all()}
    return render_template('attendance.html', group=group, students=students, records=records, att_date=att_date)

@bp.route('/attendance/<int:group_id>/mark', methods=['POST'])
@login_required
def attendance_mark(group_id):
    group = Group.query.get_or_404(group_id)
    att_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date() if request.form['date'] else date.today()
    for student in group.students.all():
        status = request.form.get(f"present_{student.id}") == 'on'
        a = Attendance.query.filter_by(group_id=group.id, student_id=student.id, date=att_date).first()
        if not a:
            a = Attendance(group_id=group.id, student_id=student.id, date=att_date, present=status)
        else:
            a.present = status
        db.session.add(a)
    db.session.commit()
    flash('Посещаемость обновлена', 'success')
    return redirect(url_for('.attendance', group_id=group.id, date=att_date))

@bp.route('/homeworks/<int:group_id>')
@login_required
def homework_list(group_id):
    group = Group.query.get_or_404(group_id)
    homeworks = group.homeworks.order_by(Homework.publish_date.desc()).all()
    editable = current_user.role == 'teacher' or current_user.role == 'admin'
    return render_template('homework_list.html', group=group, homeworks=homeworks, editable=editable)

@bp.route('/homework/<int:group_id>/add', methods=['GET', 'POST'])
@login_required
def homework_add(group_id):
    if current_user.role != 'teacher' and current_user.role != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('.homework_list', group_id=group_id))
    form = HomeworkForm()
    if form.validate_on_submit():
        hw = Homework(
            group_id=group_id,
            title=form.title.data,
            content=form.content.data,
            publish_date=form.publish_date.data,
            deadline=form.deadline.data
        )
        db.session.add(hw)
        db.session.commit()
        flash('Домашнее задание добавлено', 'success')
        return redirect(url_for('.homework_list', group_id=group_id))
    return render_template('homework_edit.html', form=form)

@bp.route('/homework/<int:hw_id>/edit', methods=['GET', 'POST'])
@login_required
def homework_edit(hw_id):
    hw = Homework.query.get_or_404(hw_id)
    if current_user.role != 'teacher' and current_user.role != 'admin':
        flash('Недостаточно прав', 'danger')
        return redirect(url_for('.homework_list', group_id=hw.group_id))
    form = HomeworkForm(obj=hw)
    if form.validate_on_submit():
        hw.title = form.title.data
        hw.content = form.content.data
        hw.publish_date = form.publish_date.data
        hw.deadline = form.deadline.data
        db.session.commit()
        flash('Домашнее задание обновлено', 'success')
        return redirect(url_for('.homework_list', group_id=hw.group_id))
    return render_template('homework_edit.html', form=form)

@bp.route('/homework/<int:hw_id>')
@login_required
def homework_view(hw_id):
    hw = Homework.query.get_or_404(hw_id)
    group = hw.group
    render_content = render_markdown(hw.content)
    is_student = current_user.role == 'student'
    submission = None
    can_update = False
    form = None
    if is_student:
        student = Student.query.filter_by(user_id=current_user.id, group_id=group.id).first()
        submission = StudentHomework.query.filter_by(homework_id=hw.id, student_id=student.id).first() if student else None
        can_update = hw.deadline >= date.today()
        form = HWSubmitForm()  # обязательно создайте объект формы
        if submission:
            form.github_url.data = submission.github_url  # можно предварительно заполнить поле

    return render_template(
        'homework_view.html',
        hw=hw,
        group=group,
        render_content=render_content,
        is_student=is_student,
        submission=submission,
        can_update=can_update,
        form=form  # передаем в шаблон форму
    )


@bp.route('/homework/<int:hw_id>/submit', methods=['POST'])
@login_required
def homework_submit(hw_id):
    hw = Homework.query.get_or_404(hw_id)
    if current_user.role != 'student':
        flash('Доступ только для студентов', 'danger')
        return redirect(url_for('.homework_view', hw_id=hw_id))
    student = Student.query.filter_by(user_id=current_user.id, group_id=hw.group_id).first()
    if not student:
        flash('Студент не найден', 'danger')
        return redirect(url_for('.homework_view', hw_id=hw_id))
    form = HWSubmitForm()
    if form.validate_on_submit() and hw.deadline >= date.today():
        submission = StudentHomework.query.filter_by(homework_id=hw.id, student_id=student.id).first()
        if not submission:
            submission = StudentHomework(homework_id=hw.id, student_id=student.id, github_url=form.github_url.data, submitted_date=datetime.now())
            db.session.add(submission)
        else:
            submission.github_url = form.github_url.data
            submission.submitted_date = datetime.now()
        db.session.commit()
        flash('Ссылка обновлена', 'success')
    else:
        flash('Нельзя обновить после дедлайна!', 'danger')
    return redirect(url_for('.homework_view', hw_id=hw_id))
