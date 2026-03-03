import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_hello_endpoint(client):
    """测试根路径返回正确内容"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello from SCF!" in response.data


def test_health_check(client):
    """可以添加健康检查端点"""
    # 假设你添加了/health端点
    # response = client.get('/health')
    # assert response.status_code == 200
    pass
