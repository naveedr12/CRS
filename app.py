import streamlit as st
import pandas as pd
import numpy as np
from utils import load_courses, load_json, save_json, RATINGS_FILE, INTERESTS_FILE

# -------------------------------
# Recommenders
# -------------------------------

class CourseRecommender:
    def __init__(self, courses, user_ratings):
        # Ensure string IDs
        self.courses = courses.copy()
        self.courses['course_id'] = self.courses['course_id'].astype(str)

        # Normalize ratings keys
        self.user_ratings = {
            user: {str(cid): rating for cid, rating in ratings.items()}
            for user, ratings in user_ratings.items()
        }

    def add_rating(self, user, course_id, rating):
        course_id = str(course_id)
        if user not in self.user_ratings:
            self.user_ratings[user] = {}
        self.user_ratings[user][course_id] = rating

    def recommend(self, user, top_n=3):
        if user not in self.user_ratings:
            return []

        # Calculate similarities
        similarities = {}
        for other_user, ratings in self.user_ratings.items():
            if other_user == user:
                continue
            sim = self._cosine_similarity(self.user_ratings[user], ratings)
            similarities[other_user] = sim

        if not similarities:
            return []

        # Score unrated courses
        scores = {}
        for other_user, sim in similarities.items():
            for course_id, rating in self.user_ratings[other_user].items():
                if course_id not in self.user_ratings[user]:
                    scores[course_id] = scores.get(course_id, 0) + sim * rating

        # Get top N IDs
        recommended_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Convert IDs to names safely
        recommended_courses = []
        for course_id, _ in recommended_ids:
            course_row = self.courses[self.courses['course_id'] == course_id]
            if not course_row.empty:
                recommended_courses.append(course_row['course_name'].values[0])
            else:
                print(f"[WARN] Missing course_id {course_id} in dataset")

        return recommended_courses

    def _cosine_similarity(self, ratings_a, ratings_b):
        all_courses = set(ratings_a.keys()).union(ratings_b.keys())
        vec_a = np.array([ratings_a.get(c, 0) for c in all_courses])
        vec_b = np.array([ratings_b.get(c, 0) for c in all_courses])

        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)


class InterestRecommender:
    def __init__(self, courses, user_interests):
        self.courses = courses.copy()
        self.courses['course_id'] = self.courses['course_id'].astype(str)
        self.courses['category'] = self.courses['category'].astype(str)

        # Normalize existing user interests
        self.user_interests = {
            user: [i.strip().lower() for i in interests]
            for user, interests in user_interests.items()
        }

    def set_interests(self, user, interests):
        self.user_interests[user] = [i.strip().lower() for i in interests]

    def recommend_by_interest(self, user, top_n=3):
        if user not in self.user_interests or not self.user_interests[user]:
            return []

        interests = self.user_interests[user]

        scores = []
        for _, row in self.courses.iterrows():
            name = str(row['course_name']).lower()
            category = str(row['category']).lower()

            # Score: count how many interests appear
            score = sum(1 for i in interests if i in name or i in category)
            if score > 0:
                scores.append((row['course_name'], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [course for course, _ in scores[:top_n]]


# -------------------------------
# App logic
# -------------------------------

# Load data
courses = load_courses()
courses['course_id'] = courses['course_id'].astype(str)  # enforce string IDs

user_ratings = load_json(RATINGS_FILE)
user_interests = load_json(INTERESTS_FILE)

# Initialize recommenders
recommender = CourseRecommender(courses, user_ratings)
interest_recommender = InterestRecommender(courses, user_interests)

# --- Streamlit UI ---
st.title("📚 Course Recommendation System")

# Sidebar: User
username = st.sidebar.text_input("Enter your name", value="Guest")

# Tabs
tab1, tab2, tab3 = st.tabs(["Rate Courses", "Set Interests", "Recommendations"])

# --- Tab 1: Rate Courses ---
with tab1:
    st.header("Rate Courses")
    for _, row in courses.iterrows():
        course_id = str(row['course_id'])
        course_name = row['course_name']
        rating = st.slider(f"{course_name} ({row['category']})", 0, 5, 0)
        if rating > 0:
            recommender.add_rating(username, course_id, rating)

    if st.button("Save Ratings"):
        save_json(recommender.user_ratings, RATINGS_FILE)
        st.success("Ratings saved!")

# --- Tab 2: Set Interests ---
with tab2:
    st.header("Set Interests")
    interests_input = st.text_input("Enter your interests (comma-separated)", value="")
    if st.button("Save Interests"):
        interests = [i.strip() for i in interests_input.split(",") if i.strip()]
        interest_recommender.set_interests(username, interests)
        save_json(interest_recommender.user_interests, INTERESTS_FILE)
        st.success("Interests saved!")

# --- Tab 3: Recommendations ---
with tab3:
    st.header("Recommendations")

    # Ratings-based
    rating_recs = recommender.recommend(username)
    st.subheader("Based on Ratings")
    if rating_recs:
        st.write("\n".join([f"- {course}" for course in rating_recs]))
    else:
        st.info("Rate some courses to get recommendations.")

    # Interest-based
    interest_recs = interest_recommender.recommend_by_interest(username)
    st.subheader("Based on Interests")
    if interest_recs:
        st.write("\n".join([f"- {course}" for course in interest_recs]))
    else:
        st.info("Set interests to get recommendations.")
