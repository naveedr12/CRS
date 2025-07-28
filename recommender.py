import numpy as np
import pandas as pd

class CourseRecommender:
    def __init__(self, courses, user_ratings):
        """
        courses: pandas DataFrame with columns ['course_id', 'course_name']
        user_ratings: dict like { 'user1': {'101': 5, '102': 3}, ... }
        """
        # Ensure course_id is string for matching
        self.courses = courses.copy()
        self.courses['course_id'] = self.courses['course_id'].astype(str)

        # Convert user_ratings keys to string too
        self.user_ratings = {
            user: {str(cid): rating for cid, rating in ratings.items()}
            for user, ratings in user_ratings.items()
        }

    def add_rating(self, user, course_id, rating):
        """Add or update a rating for a course by a user"""
        course_id = str(course_id)  # ensure consistent type
        if user not in self.user_ratings:
            self.user_ratings[user] = {}
        self.user_ratings[user][course_id] = rating

    def recommend(self, user, top_n=3):
        """Recommend top N courses for a user based on cosine similarity"""
        if user not in self.user_ratings:
            return []

        # Step 1: Calculate similarities with other users
        similarities = {}
        for other_user, ratings in self.user_ratings.items():
            if other_user == user:
                continue
            sim = self._cosine_similarity(self.user_ratings[user], ratings)
            similarities[other_user] = sim

        if not similarities:
            return []

        # Step 2: Score courses not yet rated by this user
        scores = {}
        for other_user, sim in similarities.items():
            for course_id, rating in self.user_ratings[other_user].items():
                if course_id not in self.user_ratings[user]:
                    scores[course_id] = scores.get(course_id, 0) + sim * rating

        # Step 3: Get top N recommendations
        recommended_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Step 4: Convert IDs to course names safely
        recommended_courses = []
        for course_id, _ in recommended_ids:
            course_row = self.courses[self.courses['course_id'] == course_id]
            if not course_row.empty:
                recommended_courses.append(course_row['course_name'].values[0])
            else:
                print(f"[WARN] Course ID {course_id} not found in dataset")

        return recommended_courses

    def _cosine_similarity(self, ratings_a, ratings_b):
        """Compute cosine similarity between two users' rating dicts"""
        all_courses = set(ratings_a.keys()).union(ratings_b.keys())
        vec_a = np.array([ratings_a.get(c, 0) for c in all_courses])
        vec_b = np.array([ratings_b.get(c, 0) for c in all_courses])

        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0
        return np.dot(vec_a, vec_b) / (norm_a * norm_b)
