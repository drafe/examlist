from django.db.models import QuerySet

from listsapp.models import Subject, AcademicPlan


class FuzzySubjectsComparison:
    """
    Класс, реализующий сравнение названий дисциплин для новой специальности с существующими дисциплинами из базы
    ____________
    конструктор:
    compare_sub : list[str] - список названий дисциплин
    ____________
    формат выхода:
    similar_sub : dict[ subject: similar_subjects ] - словарь с ключами-названиями дисциплин
    и значениями-листами пар (оценка; объект Subject)
    """
    MIN_WORLD_LENGTH = 3
    THRESHOLD_SENTENCE = 0.25
    THRESHOLD_WORD = 0.45
    NGRAM_LENGTH = 2

    def __init__(self, sub_to_compare: list):
        self.compare = sub_to_compare
        self.current = Subject.objects.all()

    def compareAll(self):
        d = [
            sorted(list(filter(lambda x: x[0] > 0, [(self.getFuzzyEqualValue(i, j.subject), j) for j in self.current])),
                   key=lambda x: x[0], reverse=True)
            for i in self.compare]
        return d

    @staticmethod
    def normal(s: str):
        return "".join(c for c in s if c.isalnum()).lower()

    @staticmethod
    def words(s: str):
        f = FuzzySubjectsComparison
        return [f.normal(_) for _ in s.split(' ') if len(_) >= f.MIN_WORLD_LENGTH]

    @staticmethod
    def isWordsFuzzyEqual(first: str, second: str):
        if first == second:
            return True

        f = FuzzySubjectsComparison
        equalNgram = 0
        first_gram_count = len(first) - f.NGRAM_LENGTH + 1
        second_gram_count = len(second) - f.NGRAM_LENGTH + 1
        used_ngram = [False for _ in range(second_gram_count)]

        for i in range(first_gram_count):
            first_gram = first[i:i + f.NGRAM_LENGTH]
            for j in range(second_gram_count):
                if not used_ngram[j]:
                    second_gram = second[j:j + f.NGRAM_LENGTH]
                    if first_gram == second_gram:
                        equalNgram += 1
                        used_ngram[j] = True
                        break
        tanimoto = equalNgram / (first_gram_count + second_gram_count - equalNgram)
        return tanimoto >= f.THRESHOLD_WORD

    @staticmethod
    def getFuzzyEqualValue(first: str, second: str):
        f = FuzzySubjectsComparison
        if (not first and not second) or (f.normal(first) == f.normal(second)):
            return 1.0

        if not first or not second:
            return 0.0

        equalWords = 0
        first_words = f.words(first)
        second_words = f.words(second)
        used_words = [False for _ in range(len(second_words))]

        for i in first_words:
            for _, j in enumerate(second_words):
                if not used_words[_]:
                    if f.isWordsFuzzyEqual(i, j):
                        equalWords += 1
                        used_words[_] = True
                        break

        return equalWords / (len(first_words) + len(second_words) - equalWords)


class AcademicDifferenceComparison:
    THRESHOLD_SENSITIVITY = 0.3

    def __init__(self, from_specialty, from_semester, to_specialty, to_semester):
        _from = AcademicPlan.objects.select_related('id_subject').filter(
            id_specialty=from_specialty, semester__lte=from_semester)
        _to = AcademicPlan.objects.select_related('id_subject').filter(
            id_specialty=to_specialty, semester__lte=to_semester)
        self._to_same = _to.filter(id_subject__in=_from.values('id_subject')).order_by('id_subject')
        self._from_same = _from.filter(id_subject__in=_to.values('id_subject')).order_by('id_subject')
        self._from_diff = _from.exclude(id__in=self._from_same)
        self._to_diff = _to.exclude(id__in=self._to_same)

    def compare(self):
        def hours(plan: AcademicPlan):
            return plan.h_practice + plan.h_lecture + plan.h_laboratory

        compare_same = [dict(is_differ=False, academic=t)
                        if hours(f) - hours(t) > -1 else
                        dict(is_differ=True, academic=t)
                        for f, t in zip(self._from_same, self._to_same)]

        f = FuzzySubjectsComparison

        d = [sorted(
                list(
                    filter(
                        lambda x: x[0] > self.THRESHOLD_SENSITIVITY,
                        [(f.getFuzzyEqualValue(i.id_subject.subject, j.id_subject.subject), j)
                         for j in self._from_diff]
                    )
                ),
            key=lambda x: x[0], reverse=True)
            for i in self._to_diff]

        compare_diff = [
            dict(is_differ=False, academic=t)
            if len(f) and hours(f[0][1]) - hours(t) > -1 else
            dict(is_differ=True, academic=t)
            for f, t in zip(d, self._to_diff)
        ]

        return compare_same + compare_diff


if '__name__' == '__main__':
    s = ['Иностранный язык', 'История', 'Философия', 'Иностранный язык в профессиональной сфере',
         'Математика', 'Физика', 'Информатика и информационно-коммуникационные технологии',
         'Правоведение', 'Экономика', 'Дискретная математика',
         'Математическая логика',
         'История науки и техники / Культурология', 'Методика преподавания / Педагогика',
         'Социология и политология / Религиоведение', 'Операционные системы',
         'Электротехника, электроника и схемотехника', 'Базы данных', 'Сети и телекоммуникации',
         'Основы программирования', 'Безопасность жизнедеятельности', 'Основы охраны труда',
         'Программирование', 'Web-программирование',
         'СУБД Oracle', 'Объектно-ориентированное программирование',
         'Современные информационные системы и технологии', 'Инженерная и компьютерная графика',
         'Архитектура ЭВМ и микроконтроллеров', 'ЭВМ и периферийные устройства',
         'Программирование в системе "1С: Предприятие" / Администрирование системы "1С: Предприятие" / Компьютерный дизайн',
         'Вычислительная математика  / Численные методы /Вычислительные методы',
         'Программирование робототехнических систем / Администрирование операционных систем /  Программные средства обработки графической информации',
         'Интернет-технологии /  Аппаратные средства локальных сетей / Web-дизайн',
         'Программирование в Unix / Администрирование распределённых систем / Компьютерная анимация и видео']
    print(FuzzySubjectsComparison(s).compareAll())
