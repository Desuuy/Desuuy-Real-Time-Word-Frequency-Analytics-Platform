import streamlit as st
import requests
import redis
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PRODUCER_API_URL = os.getenv('PRODUCER_API_URL', 'http://localhost:8000')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

# Page configuration
st.set_page_config(
    page_title="Real-Time Word Frequency Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for tracking refreshes and user preferences
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = True
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0
if 'word_counts_cache' not in st.session_state:
    st.session_state.word_counts_cache = {}
if 'metadata_cache' not in st.session_state:
    st.session_state.metadata_cache = {}
if 'table_search_value' not in st.session_state:
    st.session_state.table_search_value = ""
if 'next_refresh_time' not in st.session_state:
    st.session_state.next_refresh_time = time.time() + 3  # Default 3 seconds
if 'text_input_value' not in st.session_state:
    st.session_state.text_input_value = ""

# Initialize Redis connection
@st.cache_resource
def init_redis():
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        redis_client.ping()  # Test connection
        return redis_client
    except Exception as e:
        st.error(f"Failed to connect to Redis: {e}")
        return None

def submit_text_to_api(text, user_id):
    """Submit text to the producer API"""
    try:
        response = requests.post(
            f"{PRODUCER_API_URL}/submit_text",
            json={"text": text, "user_id": user_id},
            timeout=10
        )
        return response.json(), response.status_code == 200
    except Exception as e:
        return {"error": str(e)}, False

def get_word_counts(redis_client):
    """Get current word counts from Redis with caching"""
    try:
        if redis_client is None:
            # Return cached data if Redis is unavailable
            return st.session_state.word_counts_cache, st.session_state.metadata_cache
        
        # Get word counts
        word_counts_str = redis_client.get('word_counts')
        word_counts = json.loads(word_counts_str) if word_counts_str else {}
        
        # Get metadata
        metadata_str = redis_client.get('word_counts_metadata')
        metadata = json.loads(metadata_str) if metadata_str else {}
        
        # Update cache if we got new data
        if word_counts:
            st.session_state.word_counts_cache = word_counts
        if metadata:
            st.session_state.metadata_cache = metadata
        
        # Return current data or cached data if empty
        return (word_counts or st.session_state.word_counts_cache, 
                metadata or st.session_state.metadata_cache)
    except Exception as e:
        logger.error(f"Error getting word counts: {e}")
        # Return cached data on error
        return st.session_state.word_counts_cache, st.session_state.metadata_cache

def check_api_health():
    """Check API health status"""
    try:
        response = requests.get(f"{PRODUCER_API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    # Title and header with improved styling
    st.title("🔥 Real-Time Word Frequency Dashboard")
    st.markdown("""
    <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h4 style="color: #1f77b4; margin: 0;">📊 Live Analytics for Text Processing</h4>
        <p style="margin: 0.5rem 0 0 0; color: #666;">
            Submit text and watch word frequencies update in real-time using Apache Kafka, 
            PySpark Structured Streaming, and Redis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize Redis
    redis_client = init_redis()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Auto-refresh controls
        col1, col2 = st.columns(2)
        with col1:
            auto_refresh = st.checkbox(
                "Auto-refresh", 
                value=st.session_state.auto_refresh_enabled,
                key="auto_refresh_checkbox"
            )
        with col2:
            refresh_interval = st.slider("Interval (s)", 1, 10, 3, key="refresh_interval")
        
        # Update session state
        st.session_state.auto_refresh_enabled = auto_refresh
        
        # Manual refresh button
        if st.button("🔄 Refresh Now", type="secondary"):
            st.session_state.refresh_counter += 1
            st.rerun()
        
        # Display settings
        st.subheader("Display Settings")
        max_words = st.slider("Max words to display", 10, 100, 20, key="max_words")
        min_frequency = st.slider("Min word frequency", 1, 10, 1, key="min_frequency")
        
        # Search functionality
        st.subheader("🔍 Search")
        search_word = st.text_input("Search for specific word:", key="search_word")
        
        # System health status
        st.subheader("🏥 System Health")
        api_healthy = check_api_health()
        
        if api_healthy:
            st.success("✅ Producer API: Online")
        else:
            st.error("❌ Producer API: Offline")
        
        if redis_client:
            st.success("✅ Redis: Connected")
        else:
            st.error("❌ Redis: Disconnected")
        
        # Last refresh info
        st.subheader("📊 Refresh Info")
        st.text(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        st.text(f"Refresh count: {st.session_state.refresh_counter}")
    
    # Text input section
    st.header("📝 Submit Text")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Initialize text value from session state
        if 'text_input_value' not in st.session_state:
            st.session_state.text_input_value = ""
        
        user_text = st.text_area(
            "Enter your text here:",
            value=st.session_state.text_input_value,
            placeholder="Type anything... Your words will be counted in real-time!",
            height=100,
            key="user_text_input"
        )
        
        # Update session state with current text value
        st.session_state.text_input_value = user_text
    
    with col2:
        user_id = st.text_input("User ID:", value="anonymous", key="user_id_input")
        submit_button = st.button("🚀 Submit Text", type="primary")
    
    # Handle text submission
    if submit_button and user_text.strip():
        with st.spinner("Submitting text..."):
            result, success = submit_text_to_api(user_text.strip(), user_id)
            
            if success:
                st.success("✅ Text submitted successfully!")
                st.balloons()
                # Clear the text input by updating session state
                st.session_state.text_input_value = ""
                # Trigger a refresh after submission
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ Failed to submit text: {result.get('detail', 'Unknown error')}")
    
    # Dashboard section
    st.header("📊 Live Word Frequency Dashboard")
    
    # Get current data
    word_counts, metadata = get_word_counts(redis_client)
    
    if not word_counts:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #fafafa; border-radius: 1rem; margin: 2rem 0;">
            <h3 style="color: #666;">💭 No word data available yet</h3>
            <p style="font-size: 1.1rem; color: #888; margin-bottom: 2rem;">
                Submit some text above to see the magic happen! Your text will be processed in real-time
                using Apache Kafka and PySpark, then visualized here instantly.
            </p>
            <div style="background-color: #747A7E; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                <strong>💡 Try this:</strong> Type "The quick brown fox jumps over the lazy dog" to see how it works!
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Unique Words", len(word_counts))
        
        with col2:
            total_count = sum(word_counts.values())
            st.metric("Total Word Count", total_count)
        
        with col3:
            if metadata.get('last_updated'):
                try:
                    last_updated = datetime.fromisoformat(metadata['last_updated'].replace('Z', '+00:00'))
                    st.metric("Last Updated", last_updated.strftime("%H:%M:%S"))
                except:
                    st.metric("Last Updated", "Unknown")
            else:
                st.metric("Last Updated", "No data")
        
        with col4:
            if metadata.get('processed_records'):
                st.metric("Records Processed", metadata['processed_records'])
            else:
                st.metric("Records Processed", 0)
        
        # Filter and prepare data
        filtered_counts = {
            word: count for word, count in word_counts.items() 
            if count >= min_frequency and len(word) > 2
        }
        
        # Apply search filter
        if search_word and search_word.strip():
            search_results = {
                word: count for word, count in filtered_counts.items()
                if search_word.lower() in word.lower()
            }
            if search_results:
                filtered_counts = search_results
                st.info(f"🔍 Showing results for '{search_word}': {len(search_results)} matches")
            else:
                st.warning(f"🔍 No results found for '{search_word}'")
                filtered_counts = {}
        
        if filtered_counts:
            # Sort by frequency and limit
            sorted_words = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)[:max_words]
            
            # Create DataFrame
            df = pd.DataFrame(sorted_words, columns=['Word', 'Frequency'])
            
            # Charts section
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("📊 Top Words (Bar Chart)")
                fig_bar = px.bar(
                    df, 
                    x='Word', 
                    y='Frequency',
                    color='Frequency',
                    color_continuous_scale='viridis',
                    title=f"Top {len(df)} Most Frequent Words"
                )
                fig_bar.update_layout(height=400, showlegend=False)
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with chart_col2:
                st.subheader("🥧 Word Distribution (Pie Chart)")
                # Limit pie chart to top 10 for better readability
                pie_df = df.head(10)
                fig_pie = px.pie(
                    pie_df, 
                    values='Frequency', 
                    names='Word',
                    title=f"Distribution of Top {len(pie_df)} Words"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Data table section
            st.subheader("📋 Word Frequency Table")
            
            # Table search functionality
            table_search = st.text_input(
                "🔍 Filter table:", 
                value=st.session_state.table_search_value,
                placeholder="Search words in the table..."
            )
            
            # Update session state
            if table_search != st.session_state.table_search_value:
                st.session_state.table_search_value = table_search
            
            display_df = df
            if table_search and table_search.strip():
                display_df = df[df['Word'].str.contains(table_search.strip(), case=False, na=False)]
                if len(display_df) == 0:
                    st.warning(f"No words found matching '{table_search}'")
                else:
                    st.info(f"Found {len(display_df)} words matching '{table_search}'")
            
            # Display the table
            st.dataframe(
                display_df,
                use_container_width=True,
                height=300
            )
            
            # Download section
            st.subheader("📥 Export Data")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="� Download CSV",
                    data=csv_data,
                    file_name=f"word_frequencies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name=f"word_frequencies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col3:
                # Show data summary
                st.metric("Showing Words", len(display_df))
        else:
            st.info("🔍 No words match the current filters. Try adjusting your search criteria.")
    
    # Auto-refresh logic with improved stability
    if auto_refresh:
        # Show refresh status in sidebar
        with st.sidebar:
            st.divider()
            st.write(f"🔄 Auto-refresh: ON ({refresh_interval}s)")
            
            # Calculate time until next refresh
            current_time = time.time()
            if st.session_state.next_refresh_time > current_time:
                time_left = int(st.session_state.next_refresh_time - current_time)
                st.write(f"⏱️ Next refresh in: {time_left}s")
            else:
                st.write("🔄 Refreshing...")
            
            # Add pause button
            if st.button("⏸️ Pause Auto-refresh"):
                st.session_state.auto_refresh_enabled = False
                st.rerun()
        
        # Check if it's time to refresh
        current_time = time.time()
        if current_time >= st.session_state.next_refresh_time:
            st.session_state.next_refresh_time = current_time + refresh_interval
            st.session_state.refresh_counter += 1
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    else:
        # Show manual refresh option when auto-refresh is off
        with st.sidebar:
            st.divider()
            st.write("⏸️ Auto-refresh: OFF")
            if st.button("🔄 Manual Refresh"):
                st.session_state.refresh_counter += 1
                st.session_state.last_refresh = datetime.now()
                st.rerun()

if __name__ == "__main__":
    main()
