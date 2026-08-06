from core.memory_manager import remember, recall


def test_memory():

    remember("test", "hello")

    result = recall("test")

    assert result == "hello"


if __name__ == "__main__":
    test_memory()
    print("Memory test passed!")