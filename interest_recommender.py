class InterestRecommender:
    def __init__(self, courses, user_interests):
        # Ensure course_id is string and normalize category names
        self.courses = courses.copy()
        self.courses['course_id'] = self.courses['course_id'].astype(str)
        self.courses['category'] = self.courses['category'].astype(str)

        # Normalize existing user_interests (lowercase)
        self.user_interests = {
            user: [i.strip().lower() for i in interests]
            for user, interests in user_interests.items()
        }

    def set_interests(self, user, interests):
        # Store interests in lowercase for matching
        self.user_interests[user] = [i.strip().lower() for i in interests]

    def recommend_by_interest(self, user, top_n=3):
        if user not in self.user_interests or not self.user_interests[user]:
            return []

        interests = self.user_interests[user]

        scores = []
        for _, row in self.courses.iterrows():
            # Normalize for matching
            name = str(row['course_name']).lower()
            category = str(row['category']).lower()

            # Score based on keyword presence
            score = sum(1 for i in interests if i in name or i in category)
            if score > 0:
                scores.append((row['course_name'], score))

        # Sort by highest score
        scores.sort(key=lambda x: x[1], reverse=True)
        return [course for course, _ in scores[:top_n]]
