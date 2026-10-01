"""Модель для оценки сообщений и функция которая ей пользуется."""

# ~нейросеть - настоящую писать долго - так что будет игрушечная, 
# у модели есть словарик любимых слов, и она оценивает сообщение
# по самому лучшему слову которое в нем встретилось

WORD_RATES = {
    "чапаев": 0.95,
    "пустота": 0.9,
    "python": 1.0,
    "кот": 0.7,
    "хорошо": 0.85,
}
UNKNOWN_WORD = 0.1  # незнакомые слова модель не любит


class SomeModel:
    """Та самая модель. пока знает всего несколько слов."""

    def predict(self, message: str) -> float:
        # lower - Чапаев и чапаев считаются одним словом
        words = message.lower().split()
        if not words:
            return 0.0
        return max(WORD_RATES.get(word, UNKNOWN_WORD) for word in words)


def predict_message_mood(
    message: str,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> str:
    """Говорит насколько хорошее сообщение: неуд, норм или отл."""
    model = SomeModel()
    rate = model.predict(message)

    if rate < bad_thresholds:
        return "неуд"
    if rate > good_thresholds:
        return "отл"
    return "норм"
