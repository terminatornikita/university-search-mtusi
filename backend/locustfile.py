from locust import HttpUser, task, between

class SearchUser(HttpUser):
    """Нагрузочное тестирование: 50 пользователей ищут документы."""
    wait_time = between(1, 3)

    @task(3)
    def search_engineering(self):
        self.client.get("/api/v1/search?q=программная+инженерия")

    @task(2)
    def search_architecture(self):
        self.client.get("/api/v1/search?q=архитектура+микросервисов")

    @task(1)
    def search_docker(self):
        self.client.get("/api/v1/search?q=Docker")
