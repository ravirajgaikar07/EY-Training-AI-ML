import sqlite3

DB_PATH = "creator_ai.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Update Neelam's username
cursor.execute("""
UPDATE creators
SET user_name = ?
WHERE display_name = ?
""", ("neelam.ai", "Neelam Pawar"))

# Update Raviraj's username (replace 'Raviraj' with the exact display_name in your DB)
cursor.execute("""
UPDATE creators
SET user_name = ?
WHERE display_name = ?
""", ("raviraj.ai", "Raviraj Gaikar"))  # Or "Raviraj" if that's the correct name

conn.commit()
conn.close()
print("✅ Usernames updated successfully.")


#
# # Create table with your latest schema
# cursor.execute("""
# CREATE TABLE creators (
#     creator_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     display_name TEXT,
#     user_name TEXT,
#     email TEXT,
#     phone_number TEXT,
#     niches TEXT,
#     category TEXT,
#     followers_count INTEGER,
#     audience_geography TEXT,
#     reel_engagement REAL,
#     post_engagement REAL,
#     story_engagement REAL,
#     external_linktap REAL,
#     embedding TEXT
# )
# """)
#
# print("✅ Table 'creators' created successfully.")
#
# # Sample creators (added user_name, category, followers_count)
# sample_creators = [
#     ("Neelam Pawar", "neelam.p", "neelamp1225@gmail.com", "+91-9876543210", "beauty, skincare", "makeup reviews", 120000, "India, UAE", 75, 62, 81, 45, None),
#     ("Rohan Mehta", "fit.rohan", "rohan.mehta@example.com", "+91-9123456780", "fitness, lifestyle", "home workouts", 95000, "India, Singapore", 85, 71, 66, 54, None),
#     ("Sara Khan", "sarak.travels", "sara.khan@example.com", "+91-9988776655", "travel, vlog", "travel hacks", 87000, "India, Thailand, Nepal", 92, 78, 89, 51, None),
#     ("Ankit Sharma", "ankit.tech", "ankit.sharma@example.com", "+91-9090909090", "tech, gadgets", "tech reviews", 110000, "India, US, UK", 63, 58, 61, 42, None),
#     ("Priya Nair", "stylebypriya", "priya.nair@example.com", "+91-9811122233", "fashion, lifestyle", "outfit guides", 102000, "India, Dubai", 82, 72, 67, 55, None),
#     ("Karan Desai", "karan.fin", "karan.desai@example.com", "+91-9812233445", "finance, investing", "personal finance", 91000, "India", 64, 51, 56, 37, None),
#     ("Nisha Patil", "foodbynisha", "nisha.patil@example.com", "+91-9911001100", "food, recipes", "healthy recipes", 98000, "India, UK", 89, 77, 82, 61, None),
#     ("Ravi Kumar", "ravi.autos", "ravi.kumar@example.com", "+91-8877665544", "automobile, vlog", "car reviews", 88000, "India, UAE", 78, 67, 69, 49, None),
#     ("Sneha Iyer", "learnwithsneha", "sneha.iyer@example.com", "+91-8899776655", "education, career", "study tips", 104000, "India, Canada", 72, 66, 63, 43, None),
#     ("Aman Gupta", "gameonaman", "aman.gupta@example.com", "+91-7766554433", "gaming, tech", "mobile gaming", 115000, "India, Philippines", 91, 83, 77, 59, None),
#     ("Meera Joshi", "artbymeera", "meera.joshi@example.com", "+91-9988772211", "art, DIY", "craft tutorials", 97000, "India, Malaysia", 87, 79, 84, 48, None),
#     ("Devansh Kapoor", "menwithstyle", "devansh.kapoor@example.com", "+91-9099887766", "fashion, lifestyle", "men’s fashion", 89000, "India", 81, 69, 71, 52, None),
#     ("Ritika Sinha", "ritika.wellness", "ritika.sinha@example.com", "+91-7788996655", "mental health, wellness", "self-care", 76000, "India, Australia", 79, 71, 66, 47, None),
#     ("Aditya Verma", "aditya.codes", "aditya.verma@example.com", "+91-8899001122", "tech, coding", "AI tutorials", 132000, "India, US", 68, 59, 62, 41, None),
#     ("Tanvi Reddy", "tanvi.beauty", "tanvi.reddy@example.com", "+91-9988007766", "beauty, lifestyle", "fashion & makeup", 101000, "India, Singapore", 83, 71, 74, 58, None),
#     ("Arjun Singh", "fitwitharjun", "arjun.singh@example.com", "+91-7766885544", "sports, fitness", "gym motivation", 99000, "India", 88, 79, 82, 56, None),
#     ("Divya Bhat", "divya.photos", "divya.bhat@example.com", "+91-6677889900", "travel, photography", "travel photography", 108000, "India, Indonesia", 94, 85, 86, 53, None),
#     ("Harshita Jain", "harshita.reads", "harshita.jain@example.com", "+91-7766009988", "books, motivation", "book reviews", 86000, "India, UK", 74, 66, 64, 44, None),
#     ("Vikram Tiwari", "vikram.startups", "vikram.tiwari@example.com", "+91-6655443322", "tech, startups", "startup news", 118000, "India, US", 69, 61, 65, 46, None),
#     ("Neha Kapoor", "neha.parents", "neha.kapoor@example.com", "+91-7788665544", "parenting, lifestyle", "parenting tips", 97000, "India, Canada", 82, 73, 69, 51, None)
# ]
#
#
# # Insert sample creators into DB
# cursor.executemany("""
# INSERT INTO creators (
#     display_name, user_name, email, phone_number, niches, category, followers_count,
#     audience_geography, reel_engagement, post_engagement, story_engagement, external_linktap, embedding
# )
# VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# """, sample_creators)
#
# conn.commit()
# conn.close()
# print("✅ Sample creators inserted successfully.")