import streamlit as st
import pandas as pd
import io
from datetime import datetime
import numpy as np


if "statistics" not in st.session_state:
    st.session_state["statistics"] = None



# Configure page
st.set_page_config(
    page_title="LGD Trading LLP",
    page_icon="💎",
    layout="wide"
)   

st.markdown("""
<style>
/* 🌊 White background with subtle wave texture */
.stApp {
    background: #d3edd7;
    background-image: url("https://www.transparenttextures.com/patterns/skulls.png");
    background-repeat: repeat;
    font-family: 'Segoe UI', sans-serif;
}

/* 🌊 Slowly shift the wave pattern */
@keyframes waveShift {
    0% { background-position: 0 0; }
    100% { background-position: 800px 400px; }
}
/* 🧊 White glass container */
.block-container {
    max-width: 1500px;
    margin: 3rem auto;
    padding: 2rem;

    background: rgba(255, 255, 255, 0.3);  /* translucent white */
    backdrop-filter: blur(0.5px);
    -webkit-backdrop-filter: blur(0.5px);

    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);

    position: relative;
    z-index: 1;
}

/* 🔤 Text remains black for readability */
html, body, h1, h2, h3, h4, h5, p, label, span, div {
    color: #111 !important;
}
            
@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(0, 255, 200, 0.2);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 255, 200, 0.5);
  }
}

button {
    position: relative;
    animation: pulseGlow 3s ease-in-out infinite;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #0f1113 !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 0.65rem 1.3rem;
    font-weight: 600;
    overflow: hidden;
    z-index: 1;
    transition: all 0.3s ease;
}

/* 🔮 Animated glow border on hover */
button::before {
    content: "";
    position: absolute;
    top: -2px; left: -2px;
    width: calc(100% + 4px);
    height: calc(100% + 4px);
    border-radius: inherit;
    background: linear-gradient(135deg, #00ffc3, #4a00e0);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: -1;
    filter: blur(8px);
}

/* 🎨 Gradient swipe in on hover */
button:hover::before {
    opacity: 1;
}

/* ✨ Text color change on hover */
button:hover {
    color: #ffffff !important;
    border-color: rgba(0, 255, 195, 0.4);
}

/* 🔘 Browse files button */
section[data-testid="stFileUploader"] .css-1jfc3zo {
    background-color: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #111 !important;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
}

section[data-testid="stFileUploader"] .css-1jfc3zo:hover {
    background-color: rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}

</style>
""", unsafe_allow_html=True)





def validate_master_file(df):
    """Validate master file has required columns"""
    required_columns = ['Shape', 'From Size', 'To Size', 'Color', 'Clarity', 'Grid', 'Available', 'On Memo', '3 MONTH SOLD PCS']
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns

def validate_pool_file(df):
    """Validate pool file has required columns"""
    required_columns = ['STOCKID', 'Shape', 'Size', 'Color', 'Clarity']
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns

def process_stones_selection(master_df, pool_df):
    """Process stone selection based on the provided algorithm"""
    
    # Create a copy of pool to avoid modifying original
    pool = pool_df.copy()
    
    # Add empty columns to pool
    pool['Grid'] = ''
    pool['Available'] = ''
    pool['On Memo'] = ''
    pool['3 MONTH SOLD PCS'] = ''
    pool['Remark'] = ''
    
    # Process each row in master file
    for idx, row in master_df.iterrows():
        shape = row['Shape']
        from_size = row['From Size']
        to_size = row['To Size']
        color = row['Color']
        clarity = row['Clarity']
        required = row['Grid']
        available = row['Available']
        memo = row['On Memo']
        sold = row['3 MONTH SOLD PCS']
        
        remaining = required - available
        
        # Filter matching pool rows (regardless of remaining)
        match_mask = (
            (pool['Shape'].str.lower() == shape.lower()) &
            (pool['Size'] >= from_size) &
            (pool['Size'] <= to_size) &
            (pool['Color'].str.upper() == color.upper()) &
            (pool['Clarity'].str.upper() == clarity.upper())
        )
        
        # Set Required and Available for all matching pool rows
        pool.loc[match_mask, 'From Size'] = from_size
        pool.loc[match_mask, 'To Size'] = to_size
        pool.loc[match_mask, 'Grid'] = required
        pool.loc[match_mask, 'Available'] = available
        pool.loc[match_mask, 'On Memo'] = memo
        pool.loc[match_mask, '3 MONTH SOLD PCS'] = sold
        
        # Fill 0 in non-matching rows for this iteration only
        inverse_mask = ~match_mask
        cols = ['Grid', 'Available', 'On Memo', '3 MONTH SOLD PCS']
        pool.loc[inverse_mask, cols] = pool.loc[inverse_mask, cols].replace('', 0)
        
        if remaining <= 0:
            continue  # nothing to select
        
        # Select unselected eligible rows
        eligible = pool[match_mask & (pool['Remark'] == '')].copy()
        
        # Sort by size ascending
        eligible = eligible.sort_values(by='Size')
        
        # Select top N rows
        selected_indices = eligible.head(int(remaining)).index
        
        # Mark as selected
        pool.loc[selected_indices, 'Remark'] = 'SELECTION'
    
    # Mark remaining blanks as Rejection
    pool.loc[pool['Remark'] == '', 'Remark'] = 'REJECTION'
    
    # Add 'Same' column with count of identical Shape + From Size + To Size + Color + Clarity combinations
    pool['Same'] = pool.groupby(
        ['Shape', 'From Size', 'To Size', 'Color', 'Clarity']
    )['Shape'].transform('count')
    
    # Add 'Group' column with 'From Size' and 'To Size' in 0.00 format
    pool['Group'] = pool.apply(
    lambda row: (
        f"{row['From Size']:.2f} - {row['To Size']:.2f}"
        if pd.notna(row['From Size']) and pd.notna(row['To Size'])
        else "-"
    ),
    axis=1
    )
    # Drop 'From Size' and 'To Size' columns
    pool.drop(columns=['From Size', 'To Size'], inplace=True)
    
    # Reorder columns as per desired output
    final_columns = [
        'STOCKID', 'Shape', 'Size', 'Color', 'Clarity',
        'Group', 'Grid', 'Available', 'On Memo', '3 MONTH SOLD PCS',
        'Same', 'Remark'
    ]
    pool = pool[final_columns]
    
    return pool

def calculate_statistics(processed_df):
    """Calculate summary statistics from processed dataframe."""
    if processed_df.empty:
        return None  # Skip if no data

    total_stones = len(processed_df)
    selections = (processed_df['Remark'] == 'SELECTION').sum()
    rejections = (processed_df['Remark'] == 'REJECTION').sum()

    grouped = processed_df.groupby(['Shape', 'Group', 'Color', 'Clarity']).agg({
        'Grid': 'first',
        'Available': 'first',
        'Remark': lambda x: (x == 'SELECTION').sum()
    }).reset_index()

    grouped['Required'] = grouped['Grid'] - grouped['Available']
    grouped['Required'] = grouped['Required'].replace(0, np.nan)  # Prevent division by zero

    grouped['Fulfillment_Rate'] = (grouped['Remark'] / grouped['Required'] * 100).clip(upper=100).round(2)
    grouped['Fulfillment_Rate'].fillna(100.0, inplace=True)  # Assume 100% if nothing required

    avg_fulfillment = grouped['Fulfillment_Rate'].mean()

    return {
        'total_stones': total_stones,
        'selections': selections,
        'rejections': rejections,
        'selection_rate': (selections / total_stones * 100) if total_stones > 0 else None,
        'avg_fulfillment': avg_fulfillment,
        'unique_requirements': len(grouped)
    }

def main(): 
        
    st.markdown("""
    <style>
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes glowPulse {
            0%, 100% {
                box-shadow: 0 0 12px rgba(255, 255, 255, 0.4),
                0 0 24px rgba(255, 255, 255, 0.3);
    
                }
            50% {
                box-shadow: 0 0 14px rgba(255, 255, 255, 0.3),
                            0 0 28px rgba(255, 255, 255, 0.4);
            }
        }

        @keyframes floatAndRotate {
            0% {
                transform: translateY(0px) rotate(0deg);
                opacity: 0.8;
            }
            50% {
                transform: translateY(-10px) rotate(180deg);
                opacity: 1;
            }
            100% {
                transform: translateY(0px) rotate(360deg);
                opacity: 0.8;
            }
        }

        .diamond-storm-container {
            position: relative;
            background: linear-gradient(45deg,
                #00FF9D,   /* neon mint */
                #5EEAD4,   /* soft aqua */
                #6CDBFA,   /* baby blue */
                #8EC5FC,   /* soft sky */
                #00C6FF,   /* electric blue */
                #FFD700,   /* classic gold */
                #C0C0C0,   /* pure silver */
                #5F72BE,   /* deep periwinkle */
                #9D4EDD,   /* violet indigo */
                #FF6AC2,   /* electric pink */
                #FFB6B9,   /* blush */
                #C3F584,   /* lime mint */
                #00DFD8,   /* aqua pop */
                #A7F0BA,   /* minty white */
                #3B82F6,   /* soft blue */
                #DAA520,   /* goldenrod */
                #D4AF37,   /* rich gold */
                #E5E4E2    /* platinum silver */
            );

            background-size: 1500% 1500%;
            animation: gradientShift 30s ease infinite,
                       glowPulse 6s ease-in-out infinite;

            padding: 24px;
            border-radius: 24px;
            text-align: center;
            color: Black;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            margin-bottom: 24px;  
            max-width: 1500px;
            margin-left: auto;
            margin-right: auto;     
            overflow: hidden;
        }

        .diamond-storm-container h1 {
            font-size: 30px;
            font-weight: 700;
            text-shadow: 0 0 6px rgba(255, 255, 255, 0.3);
            z-index: 1;
            position: relative;
        }

        .diamond-storm-container p {
            font-size: 15px;
            font-weight: 600;
            text-shadow: 0 0 4px rgba(255, 255, 255, 0.2);
            z-index: 1;
            position: relative;
        }

        .diamond {
            position: absolute;
            font-size: 16px;
            animation: floatAndRotate 6s ease-in-out infinite;
            opacity: 0.7;
            
        }
        .creator-signature {
            position: absolute;
            bottom: 10px;
            right: 14px;
            font-size: 13px;
            color: rgba(0, 0, 0, 0.75);  /* 🖤 Soft black text */
            font-family: 'Segoe UI', sans-serif;
            font-style: italic;
            letter-spacing: 0.3px;
            background-color: rgba(255, 255, 255, 0.15); /* optional highlight */
            padding: 4px 10px;
            border-radius: 8px;
            backdrop-filter: blur(2px);
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            z-index: 2;
        }

        
    </style>

    <div class="diamond-storm-container">
        <!-- Floating diamonds -->
        <span class="diamond" style="top: 10%; left: 5%; font-size: 28px; animation-delay: 0s;">💎</span>
        <span class="diamond" style="top: 15%; left: 20%; font-size: 32px; animation-delay: 0.5s;">💎</span>
        <span class="diamond" style="top: 20%; left: 70%; font-size: 26px; animation-delay: 1s;">💎</span>
        <span class="diamond" style="top: 30%; left: 10%; font-size: 30px; animation-delay: 1.5s;">💎</span>
        <span class="diamond" style="top: 40%; left: 25%; font-size: 22px; animation-delay: 2s;">💎</span>
        <span class="diamond" style="top: 50%; left: 80%; font-size: 34px; animation-delay: 2.5s;">💎</span>
        <span class="diamond" style="top: 60%; left: 15%; font-size: 29px; animation-delay: 3s;">💎</span>
        <span class="diamond" style="top: 70%; left: 60%; font-size: 31px; animation-delay: 3.5s;">💎</span>
        <span class="diamond" style="top: 75%; left: 10%; font-size: 25px; animation-delay: 4s;">💎</span>
        <span class="diamond" style="top: 85%; left: 35%; font-size: 30px; animation-delay: 4.5s;">💎</span>
        <span class="diamond" style="top: 90%; left: 80%; font-size: 28px; animation-delay: 5s;">💎</span>
        <span class="diamond" style="top: 25%; left: 90%; font-size: 24px; animation-delay: 1.2s;">💎</span>
        <span class="diamond" style="top: 5%; left: 60%; font-size: 36px; animation-delay: 0.7s;">💎</span>
        <span class="diamond" style="top: 15%; left: 45%; font-size: 27px; animation-delay: 2.3s;">💎</span>
        <span class="diamond" style="top: 35%; left: 55%; font-size: 23px; animation-delay: 3.3s;">💎</span>
        <span class="diamond" style="top: 45%; left: 65%; font-size: 33px; animation-delay: 4.1s;">💎</span>
        <span class="diamond" style="top: 55%; left: 90%; font-size: 30px; animation-delay: 5.2s;">💎</span>
        <span class="diamond" style="top: 65%; left: 5%; font-size: 26px; animation-delay: 1.6s;">💎</span>
        <span class="diamond" style="top: 78%; left: 50%; font-size: 29px; animation-delay: 3.8s;">💎</span>
        <span class="diamond" style="top: 92%; left: 20%; font-size: 35px; animation-delay: 5.5s;">💎</span>

   
    <h1> LGD Trading LLP</h1>
    <p>Automated stone selection and inventory processing</p>
    <div class="creator-signature">Designed by <strong>Neel Limbachiya</strong></div>
    </div>
    """, unsafe_allow_html=True)



    
    st.markdown("### 📁 Upload Files")

    # Upload Master File like Pool File
    master_file = st.file_uploader(
        "Upload Master Refile File",
        type=['xlsx', 'xls'],
        help="Excel file containing master stone requirement"
    )

    # Upload Pool File
    pool_file = st.file_uploader(
        "Upload File For Selections",
        type=['xlsx', 'xls'],
        help="Excel file containing available stone inventory"
    )

    # Validation
    if master_file is None or pool_file is None:
        st.info("👆 Please upload both Master and Party Excel files to begin processing")
        st.stop()

    try:
        # Load files
        with st.spinner("Loading files..."):
            master_df = pd.read_excel(master_file)
            pool_df = pd.read_excel(pool_file)

        # Validate structure
        master_valid, master_missing = validate_master_file(master_df)
        pool_valid, pool_missing = validate_pool_file(pool_df)

        if not master_valid:
            st.error(f"❌ Master file is missing required columns: {', '.join(master_missing)}")
            st.stop()

        if not pool_valid:
            st.error(f"❌ Pool file is missing required columns: {', '.join(pool_missing)}")
            st.stop()

        st.success("✅ Files loaded successfully!")
        # Show file info
        col1 = st.columns(1)[0]  # Only one column now
        with col1:
            st.metric("Available Stones", f"{len(pool_df)} stones")
             
        # Process button
        if st.button("🔄 Process Stone Selection", type="primary"):
            with st.spinner("Processing stone selection..."):
                try:
                    processed_df = process_stones_selection(master_df, pool_df)
                    
                    # Store in session state
                    st.session_state.processed_df = processed_df
                    st.session_state.statistics = calculate_statistics(processed_df)
                    
                    st.success("✅ Processing completed!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error during processing: {str(e)}")
        
        # Display results if available
        if 'processed_df' in st.session_state:
            st.markdown("---")
            st.header("📊 Results Summary")
            
            # Statistics
            stats = st.session_state.statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Stones", stats['total_stones'])
            with col2:
                st.metric("Selections", stats['selections'], 
                         f"{stats['selection_rate']:.1f}%")
            with col3:
                st.metric("Rejections", stats['rejections'])
            with col4:
                st.metric("Avg Fulfillment", f"{stats['avg_fulfillment']:.1f}%")
            
            # Results table
            st.subheader("🔍 Detailed Results")
            
            df = st.session_state.processed_df.copy()

            # Create 5 columns in one row
            col1, col2, col3, col4, col5 = st.columns(5)

            # Shape Filter
            with col1:
                shape_options = sorted(df['Shape'].dropna().unique().tolist())
                shape_filter = st.multiselect("Shape", options=shape_options)

            df_shape = df[df['Shape'].isin(shape_filter)] if shape_filter else df

            # Color Filter
            with col2:
                color_options = sorted(df_shape['Color'].dropna().unique().tolist())
                color_filter = st.multiselect("Color", options=color_options)

            df_color = df_shape[df_shape['Color'].isin(color_filter)] if color_filter else df_shape

            # Clarity Filter
            with col3:
                clarity_options = sorted(df_color['Clarity'].dropna().unique().tolist())
                clarity_filter = st.multiselect("Clarity", options=clarity_options)

            df_clarity = df_color[df_color['Clarity'].isin(clarity_filter)] if clarity_filter else df_color

            # Group Filter
            with col4:
                group_options = sorted(df_clarity['Group'].dropna().unique().tolist())
                group_filter = st.multiselect("Group", options=group_options)

            df_group = df_clarity[df_clarity['Group'].isin(group_filter)] if group_filter else df_clarity

            # Status Filter
            with col5:
                remark_options = sorted(df_group['Remark'].dropna().unique().tolist())
                remark_filter = st.multiselect("Status", options=remark_options)

            # Final filter
            filtered_df = df_group[df_group['Remark'].isin(remark_filter)] if remark_filter else df_group



            # Color code the dataframe for better visualization
            def highlight_remark(val):
                if val == 'SELECTION':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'REJECTION':
                    return 'background-color: #f8d7da; color: #721c24'
                return ''
            
            styled_df = filtered_df.style.applymap(highlight_remark, subset=['Remark'])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400
            )
            
            st.info(f"Showing {len(filtered_df)} of {len(st.session_state.processed_df)} total stones")
            
            # Download button
            st.markdown("---")
            st.subheader("📥 Export Results")
            
            # Create Excel file in memory
            output_buffer = io.BytesIO()
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                st.session_state.processed_df.to_excel(writer, sheet_name='Stone Selection Results', index=False)
                
                # Add summary sheet
                summary_df = pd.DataFrame([stats])
                summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
            
            output_buffer.seek(0)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stones_selected_output_{timestamp}.xlsx"
            
            st.download_button(
                label="Download Excel",
                data=output_buffer.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"❌ Error loading files: {str(e)}")
        st.info("Please ensure your Excel files are properly formatted and not corrupted.")

if __name__ == "__main__":
    main()
