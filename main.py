from utils import load_courses, print_courses, load_json, save_json, RATINGS_FILE, INTERESTS_FILE
from recommender import CourseRecommender
from interest_recommender import InterestRecommender
from termcolor import colored

def main():
    courses = load_courses()
    user_ratings = load_json(RATINGS_FILE)
    user_interests = load_json(INTERESTS_FILE)

    recommender = CourseRecommender(courses, user_ratings)
    interest_recommender = InterestRecommender(courses, user_interests)

    while True:
        print(colored("\n--- Course Recommendation System ---", "cyan", attrs=["bold"]))
        print("1. Rate a course")
        print("2. Get recommendations (ratings)")
        print("3. Set interests")
        print("4. Get recommendations (interests)")
        print("5. Exit")

        choice = input(colored("Choose an option: ", "yellow"))

        if choice == "1":
            user = input("Enter your name: ")
            print_courses(courses)
            course_id = int(input("Enter course ID to rate: "))
            rating = int(input("Enter rating (1-5): "))
            recommender.add_rating(user, course_id, rating)
            save_json(user_ratings, RATINGS_FILE)
            print(colored("Rating saved!", "green"))

        elif choice == "2":
            user = input("Enter your name: ")
            recs = recommender.recommend(user)
            if recs:
                print(colored("Recommended Courses (Based on Ratings):", "green"))
                for course in recs:
                    print(f"- {course}")
            else:
                print(colored("No recommendations yet. Rate more courses first!", "red"))

        elif choice == "3":
            user = input("Enter your name: ")
            interests = input("Enter your interests (comma separated): ").split(",")
            interest_recommender.set_interests(user, interests)
            save_json(user_interests, INTERESTS_FILE)
            print(colored("Interests saved!", "green"))

        elif choice == "4":
            user = input("Enter your name: ")
            recs = interest_recommender.recommend_by_interest(user)
            if recs:
                print(colored("Recommended Courses (Based on Interests):", "green"))
                for course in recs:
                    print(f"- {course}")
            else:
                print(colored("No interests found. Please set your interests first.", "red"))

        elif choice == "5":
            print(colored("Goodbye!", "cyan"))
            break

        else:
            print(colored("Invalid option.", "red"))

if __name__ == "__main__":
    main()
