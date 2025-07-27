import streamlit as st
import math
import pandas as pd
from datetime import datetime, time

# Distance calculation using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth in kilometers"""
    R = 6371.0  # Earth's radius in kilometers
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

class HobbyCirclesApp:
    def __init__(self):
        self.users = []
        self.activities = []
    
    def add_user(self, username, lat, lon, interests, bio=""):
        """Add new user to the system"""
        user = {
            'username': username,
            'lat': lat,
            'lon': lon,
            'interests': interests,
            'bio': bio,
            'join_date': datetime.now()
        }
        self.users.append(user)
        return f"Welcome {username}! Your profile is ready."
    
    def find_matches(self, username, radius_km=5, specific_interest=None):
        """Find compatible users within radius"""
        current_user = next((u for u in self.users if u['username'] == username), None)
        if not current_user:
            return []
        
        matches = []
        for user in self.users:
            if user['username'] == username:
                continue
            
            # Calculate distance
            distance = calculate_distance(
                current_user['lat'], current_user['lon'],
                user['lat'], user['lon']
            )
            
            # Check if within radius
            if distance > radius_km:
                continue
            
            # Find shared interests
            shared_interests = set(current_user['interests']).intersection(set(user['interests']))
            
            # Filter by specific interest if provided
            if specific_interest and specific_interest not in shared_interests:
                continue
            
            if shared_interests:
                matches.append({
                    'username': user['username'],
                    'distance': round(distance, 2),
                    'shared_interests': list(shared_interests),
                    'bio': user.get('bio', ''),
                    'all_interests': user['interests']
                })
        
        # Sort by distance (closest first)
        matches.sort(key=lambda x: x['distance'])
        return matches
    
    def post_activity(self, username, activity_type, description, time_slot, location=""):
        """Post a new activity request"""
        activity = {
            'id': len(self.activities) + 1,
            'username': username,
            'activity_type': activity_type,
            'description': description,
            'time_slot': time_slot,
            'location': location,
            'posted_at': datetime.now(),
            'responses': []
        }
        self.activities.append(activity)
        return activity['id']

# Initialize the app
if 'app' not in st.session_state:
    st.session_state.app = HobbyCirclesApp()
    
    # Add sample users for Hyderabad
    sample_users = [
        ("HyderabadBuddy", 17.385044, 78.486671, ["Badminton", "Food", "Board Games"], "Love exploring new places!"),
        ("SportyPal", 17.390000, 78.480000, ["Badminton", "Football", "Cycling"], "Always up for sports!"),
        ("FoodieFriend", 17.380000, 78.490000, ["Food", "Movies", "Photography"], "Foodie and movie buff"),
        ("BookLover", 17.370000, 78.480000, ["Board Games", "Reading", "Coffee"], "Coffee and books person"),
        ("TechieGeek", 17.375000, 78.485000, ["Board Games", "Gaming", "Food"], "Tech enthusiast"),
        ("OutdoorExplorer", 17.395000, 78.475000, ["Cycling", "Hiking", "Photography"], "Adventure seeker")
    ]
    
    for username, lat, lon, interests, bio in sample_users:
        st.session_state.app.add_user(username, lat, lon, interests, bio)

# Streamlit App Interface
st.set_page_config(page_title="Hobby Circles", page_icon="🎯", layout="wide")

st.title("🎯 Hobby Circles - Find Your Perfect Companion!")
st.subheader("Discover buddies for badminton, food adventures, and more in Hyderabad! 🏓🍜🎲")

# Sidebar for user selection and preferences
with st.sidebar:
    st.header("👤 Your Profile")
    
    # User selection
    username = st.selectbox(
        "Choose your username:",
        [u['username'] for u in st.session_state.app.users],
        help="Select your profile to find matches"
    )
    
    st.header("🔍 Search Preferences")
    
    # Search radius
    radius = st.slider("Search radius (km):", 1, 15, 5)
    
    # Interest filter
    if username:
        current_user = next(u for u in st.session_state.app.users if u['username'] == username)
        interest_filter = st.selectbox(
            "Focus on specific interest:",
            ["All interests"] + current_user['interests']
        )
        if interest_filter == "All interests":
            interest_filter = None

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Find Your Hobby Buddies")
    
    if st.button("🔍 Find Matches!", type="primary"):
        if username:
            matches = st.session_state.app.find_matches(
                username, 
                radius_km=radius,
                specific_interest=interest_filter
            )
            
            if matches:
                st.success(f"🎉 Found {len(matches)} perfect companions!")
                
                for i, match in enumerate(matches):
                    with st.expander(f"**{match['username']}** - {match['distance']}km away", expanded=True):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.write(f"**Bio:** {match['bio']}")
                            st.write(f"**Shared interests:** {', '.join(match['shared_interests'])}")
                            st.write(f"**All interests:** {', '.join(match['all_interests'])}")
                        
                        with col_b:
                            if st.button(f"💬 Chat", key=f"chat_{i}"):
                                st.info("Chat feature coming soon!")
                            if st.button(f"📍 Suggest Meetup", key=f"meetup_{i}"):
                                st.info("Meetup suggestion feature coming soon!")
            else:
                st.warning("🤔 No matches found. Try expanding your search radius or exploring new interests!")
        else:
            st.error("Please select a username first!")

with col2:
    st.header("📊 Your Profile")
    if username:
        current_user = next(u for u in st.session_state.app.users if u['username'] == username)
        st.write(f"**Username:** {current_user['username']}")
        st.write(f"**Bio:** {current_user['bio']}")
        st.write(f"**Interests:** {', '.join(current_user['interests'])}")
        
        # Show user's location on map
        st.subheader("📍 Your Location")
        user_location = pd.DataFrame({
            'lat': [current_user['lat']],
            'lon': [current_user['lon']]
        })
        st.map(user_location, zoom=12)

# Activity posting section
st.header("🎪 Post a New Activity")
with st.expander("Create Activity Request", expanded=False):
    activity_col1, activity_col2 = st.columns(2)
    
    with activity_col1:
        activity_type = st.selectbox(
            "Activity Type:",
            ["Badminton", "Food Exploration", "Board Games", "Movies", "Cycling", "Photography", "Other"]
        )
        
        activity_desc = st.text_input(
            "Description:",
            placeholder="e.g., Looking for badminton partner at LB Stadium"
        )
    
    with activity_col2:
        activity_time = st.selectbox(
            "When:",
            ["Right now", "This evening", "Tomorrow", "This weekend", "Next week"]
        )
        
        activity_location = st.text_input(
            "Location (optional):",
            placeholder="e.g., LB Stadium, Banjara Hills"
        )
    
    if st.button("🚀 Post Activity"):
        if username and activity_desc:
            activity_id = st.session_state.app.post_activity(
                username, activity_type, activity_desc, activity_time, activity_location
            )
            st.success(f"Activity posted! ID: {activity_id}")
        else:
            st.error("Please fill in the activity description!")

# Show recent activities
st.header("🎯 Recent Activities")
if st.session_state.app.activities:
    for activity in st.session_state.app.activities[-5:]:  # Show last 5 activities
        with st.container():
            st.write(f"**{activity['username']}** wants to do **{activity['activity_type']}**")
            st.write(f"📝 {activity['description']}")
            st.write(f"⏰ {activity['time_slot']} | 📍 {activity['location'] or 'Location TBD'}")
            st.write("---")
else:
    st.info("No activities posted yet. Be the first to create one!")
