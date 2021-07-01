from ranking.ranker import Ranker


if __name__ == "__main__":
    ranker = Ranker()
    query = input("search: ")
    results = ranker.get_result(query)
    for each in results:
        print(each)
