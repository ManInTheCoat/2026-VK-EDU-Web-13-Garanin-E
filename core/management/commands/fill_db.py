import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from django.db.models import OuterRef, Subquery, Count, IntegerField
from django.db.models.functions import Coalesce

fake = Faker()

class Command(BaseCommand):
    help = 'Заполняет базу данных фейковыми данными'

    def add_arguments(self, parser):
        parser.add_argument('--ratio', dest="ratio", type=int, required=True)

    def handle(self, *args, **options):
        ratio = options["ratio"]

        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200

        BATCH_SIZE_HEAVY = 100
        BATCH_SIZE_LIGHT = 1000

        self.stdout.write(self.style.SUCCESS(f'Начинаем генерацию данных (ratio={ratio})'))

        self.stdout.write('Создание пользователей...')
        users_to_create = []
        for i in range(users_count):
            username = f"{fake.user_name()}_{i}_{random.randint(1, 9999)}"
            users_to_create.append(User(username=username, email=fake.email(), password='fake_password'))

        User.objects.bulk_create(users_to_create, batch_size=BATCH_SIZE_HEAVY)

        user_ids = list(User.objects.values_list('id', flat=True))

        self.stdout.write('Создание профилей...')
        profiles_to_create = [Profile(user_id=u_id) for u_id in user_ids]
        Profile.objects.bulk_create(profiles_to_create, batch_size=BATCH_SIZE_LIGHT)

        self.stdout.write('Создание тегов...')
        tags_to_create = []
        for i in range(tags_count):
            tag_name = f"{fake.word()}_{i}_{random.randint(1, 9999)}"
            tags_to_create.append(Tag(name=tag_name[:50]))

        Tag.objects.bulk_create(tags_to_create, batch_size=BATCH_SIZE_LIGHT)
        tag_ids = list(Tag.objects.values_list('id', flat=True))

        self.stdout.write('Создание вопросов...')
        questions_to_create = []
        for i in range(questions_count):
            questions_to_create.append(
                Question(
                    title=fake.sentence()[:255],
                    text=fake.text(),
                    author_id=random.choice(user_ids)
                )
            )
        Question.objects.bulk_create(questions_to_create, batch_size=BATCH_SIZE_HEAVY)
        question_ids = list(Question.objects.values_list('id', flat=True))

        self.stdout.write('Привязка тегов к вопросам...')
        QuestionTag = Question.tags.through
        question_tags_to_create = []
        for q_id in question_ids:
            selected_tags = random.sample(tag_ids, random.randint(1, 3))
            for t_id in selected_tags:
                question_tags_to_create.append(QuestionTag(question_id = q_id, tag_id = t_id))
        QuestionTag.objects.bulk_create(question_tags_to_create, batch_size=BATCH_SIZE_LIGHT)

        self.stdout.write('Создание ответов...')
        answers_to_create = []
        for i in range(answers_count):
            answers_to_create.append(
                Answer(
                    text=fake.text(),
                    author_id=random.choice(user_ids),
                    question_id=random.choice(question_ids),
                    is_correct=random.choice([True, False, False, False])
                )
            )
        Answer.objects.bulk_create(answers_to_create, batch_size=BATCH_SIZE_HEAVY)
        answer_ids = list(Answer.objects.values_list('id', flat=True))

        self.stdout.write('Создание оценок для вопросов...')
        unique_question_likes = set()
        while len(unique_question_likes) < (likes_count // 2):
            unique_question_likes.add((random.choice(user_ids), random.choice(question_ids)))

        q_likes = [QuestionLike(user_id=u, question_id=q, is_like=random.choice([True, False])) for u, q in unique_question_likes]
        QuestionLike.objects.bulk_create(q_likes, batch_size=BATCH_SIZE_LIGHT)

        self.stdout.write('Создание оценок для ответов...')
        unique_answer_likes = set()
        while len(unique_answer_likes) < (likes_count // 2):
            unique_answer_likes.add((random.choice(user_ids), random.choice(answer_ids)))

        a_likes = [AnswerLike(user_id=u, answer_id=a, is_like=random.choice([True, False])) for u, a in unique_answer_likes]
        AnswerLike.objects.bulk_create(a_likes, batch_size=BATCH_SIZE_LIGHT)

        self.stdout.write('Пересчет рейтингов для вопросов и ответов...')

        q_likes = QuestionLike.objects.filter(question_id=OuterRef('pk'), is_like=True, is_active=True).values('question_id').annotate(cnt=Count('pk')).values('cnt')
        q_dislikes = QuestionLike.objects.filter(question_id=OuterRef('pk'), is_like=False, is_active=True).values('question_id').annotate(cnt=Count('pk')).values('cnt')
        Question.objects.update(
            rating=Coalesce(Subquery(q_likes, output_field=IntegerField()), 0) -
                   Coalesce(Subquery(q_dislikes, output_field=IntegerField()), 0)
        )

        a_likes = AnswerLike.objects.filter(answer_id=OuterRef('pk'), is_like=True, is_active=True).values('answer_id').annotate(cnt=Count('pk')).values('cnt')
        a_dislikes = AnswerLike.objects.filter(answer_id=OuterRef('pk'), is_like=False, is_active=True).values('answer_id').annotate(cnt=Count('pk')).values('cnt')
        Answer.objects.update(
            rating=Coalesce(Subquery(a_likes, output_field=IntegerField()), 0) -
                   Coalesce(Subquery(a_dislikes, output_field=IntegerField()), 0)
        )

        self.stdout.write('Синхронизация счетчиков ответов для вопросов...')

        ans_counts = Answer.objects.filter(
            question_id=OuterRef('pk'),
            is_active=True
        ).values('question_id').annotate(
            cnt=Count('pk')
        ).values('cnt')

        Question.objects.update(
            answers_count=Coalesce(Subquery(ans_counts, output_field=IntegerField()), 0)
        )

        self.stdout.write('Синхронизация счетчиков ответов для профилей...')
        user_answers_counts = Answer.objects.filter(
            author_id=OuterRef('user_id'),
            is_active=True
        ).values('author_id').annotate(
            cnt=Count('pk')
        ).values('cnt')

        Profile.objects.update(
            answers_count=Coalesce(Subquery(user_answers_counts, output_field=IntegerField()), 0)
        )

        self.stdout.write('Синхронизация счетчиков вопросов для тегов...')
        tags_qs = QuestionTag.objects.filter(
            tag_id=OuterRef('pk'),
            question__is_active=True
        ).values('tag_id').annotate(
            cnt=Count('question_id')
        ).values('cnt')

        Tag.objects.update(
            questions_count=Coalesce(Subquery(tags_qs, output_field=IntegerField()), 0)
        )

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))
