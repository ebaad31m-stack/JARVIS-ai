from core.intent_router import process


def test_router():

    response = process("hello")

    assert response is not None


if __name__ == "__main__":
    test_router()
    print("Router test passed!")