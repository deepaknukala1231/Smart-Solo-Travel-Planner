import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="Smart Solo Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Smart Solo Travel Budget Planner")
st.write(
    "Plan your solo trip, estimate expenses, "
    "and explore places within your budget."
)

@st.cache_data
def load_destinations():
    return pd.read_csv("destinations.csv")

try:
    df = load_destinations()
except Exception as error:
    st.error(f"Could not load destinations.csv: {error}")
    st.stop()

destinations = sorted(df["destination"].unique())

st.sidebar.header("Plan Your Trip")

destination = st.sidebar.selectbox(
    "Choose destination",
    destinations
)

days = st.sidebar.number_input(
    "Number of days",
    min_value=1,
    max_value=30,
    value=3
)

budget = st.sidebar.number_input(
    "Total budget (₹)",
    min_value=500,
    max_value=500000,
    value=5000,
    step=500
)

travel_style = st.sidebar.selectbox(
    "Travel style",
    ["Budget", "Standard", "Comfort"]
)

start_location = st.sidebar.text_input(
    "Starting city",
    value="Bengaluru"
)

# Sample daily estimates for one traveler
style_multiplier = {
    "Budget": 1.0,
    "Standard": 1.5,
    "Comfort": 2.2
}[travel_style]

places = df[df["destination"] == destination].copy()

transport = float(places["transport_per_day"].iloc[0])
stay = float(places["stay_per_day"].iloc[0])
food = float(places["food_per_day"].iloc[0])
activities = float(places["activities_per_day"].iloc[0])

daily_cost = (
    transport + stay + food + activities
) * style_multiplier

# Additional estimated one-time round-trip travel cost
intercity_travel = 1000 * style_multiplier

trip_cost = daily_cost * days + intercity_travel
remaining = budget - trip_cost

st.subheader(f"Your trip: {destination}")
st.caption(
    f"Starting city: {start_location} | "
    f"{days} days | Solo traveler | {travel_style} style"
)

col1, col2, col3 = st.columns(3)

col1.metric("Estimated total", f"₹{trip_cost:,.0f}")
col2.metric("Your budget", f"₹{budget:,.0f}")
col3.metric(
    "Budget remaining",
    f"₹{remaining:,.0f}"
)

if remaining >= 0:
    st.success("Your estimated trip is within budget!")
else:
    st.warning(
        f"You may exceed your budget by ₹{-remaining:,.0f}. "
        "Try fewer days or a lower-cost travel style."
    )

st.subheader("💰 Expense Breakdown")

expense_data = pd.DataFrame({
    "Expense": [
        "Local transport",
        "Accommodation",
        "Food",
        "Activities"
    ],
    "Estimated cost (₹)": [
        transport * days * style_multiplier,
        stay * days * style_multiplier,
        food * days * style_multiplier,
        activities * days * style_multiplier
    ]
})

expense_data.loc[len(expense_data)] = [
    "Round-trip travel allowance",
    intercity_travel
]

st.bar_chart(
    expense_data.set_index("Expense")
)

st.dataframe(
    expense_data,
    use_container_width=True,
    hide_index=True
)

st.subheader("🗓️ Day-by-Day Itinerary")

for day in range(1, int(days) + 1):
    with st.expander(f"Day {day}", expanded=(day == 1)):
        place_index = (day - 1) % len(places)
        selected_place = places.iloc[place_index]

        st.write(f"**Morning:** Visit {selected_place['place']}")
        st.write(
            "**Afternoon:** Explore nearby "
            f"{selected_place['category'].lower()} attractions."
        )
        st.write("**Evening:** Enjoy local food and return to your stay.")
        st.write(
            f"Estimated daily spending: ₹{daily_cost:,.0f}"
        )

st.subheader("📍 More places to explore")

st.dataframe(
    places[["place", "category"]],
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Estimates are illustrative. Check transport fares, "
    "accommodation prices, entry fees, and local conditions "
    "before travelling."
)
# STEP 8: Smart Destination Recommendations

st.divider()
st.header("🤖 Smart Destination Recommendations")

st.write(
    "Find destinations that may fit your budget "
    "and preferred travel interests."
)

interests = st.multiselect(
    "Choose your interests",
    ["Nature", "Beach", "Heritage"],
    default=["Nature"]
)

recommendation_days = st.number_input(
    "Days for recommended trip",
    min_value=1,
    max_value=30,
    value=3,
    key="recommendation_days"
)

recommendation_budget = st.number_input(
    "Maximum total budget (₹)",
    min_value=500,
    max_value=500000,
    value=5000,
    step=500,
    key="recommendation_budget"
)

recommendation_style = st.selectbox(
    "Preferred travel style",
    ["Budget", "Standard", "Comfort"],
    key="recommendation_style"
)

if st.button("Find Best Destinations"):

    multipliers = {
        "Budget": 1.0,
        "Standard": 1.5,
        "Comfort": 2.2
    }

    multiplier = multipliers[recommendation_style]

    results = []

    for city in destinations:

        city_places = df[df["destination"] == city]

        daily_transport = city_places["transport_per_day"].mean()
        daily_stay = city_places["stay_per_day"].mean()
        daily_food = city_places["food_per_day"].mean()
        daily_activities = city_places["activities_per_day"].mean()

        estimated_daily_cost = (
            daily_transport
            + daily_stay
            + daily_food
            + daily_activities
        ) * multiplier

        estimated_total = (
            estimated_daily_cost * recommendation_days
            + 1000 * multiplier
        )

        matching_interests = city_places[
            city_places["category"].isin(interests)
        ]

        if interests:
            interest_score = len(matching_interests)
        else:
            interest_score = len(city_places)

        if estimated_total <= recommendation_budget:
            results.append({
                "Destination": city,
                "Estimated Cost (₹)": round(estimated_total),
                "Daily Cost (₹)": round(estimated_daily_cost),
                "Matching Places": interest_score
            })

    if results:

        recommendations = pd.DataFrame(results)

        recommendations = recommendations.sort_values(
            by=["Matching Places", "Estimated Cost (₹)"],
            ascending=[False, True]
        )

        st.success(
            f"Found {len(recommendations)} destinations "
            "within your estimated budget."
        )

        st.dataframe(
            recommendations,
            use_container_width=True,
            hide_index=True
        )

        best_destination = recommendations.iloc[0]

        st.subheader("🏆 Recommended Destination")

        st.write(
            f"**{best_destination['Destination']}**"
        )

        st.write(
            "Estimated total cost: "
            f"₹{best_destination['Estimated Cost (₹)']:,}"
        )

        st.write(
            "Estimated money remaining: "
            f"₹{recommendation_budget - best_destination['Estimated Cost (₹)']:,}"
        )

    else:
        st.warning(
            "No destinations fit this estimated budget. "
            "Try increasing your budget or reducing the trip duration."
        )
        # STEP 9: Download PDF Travel Itinerary

        st.divider()
        st.header("📄 Download Your Travel Plan")

        if st.button("Generate PDF Travel Plan"):

            pdf_buffer = BytesIO()

            pdf = canvas.Canvas(
                pdf_buffer,
                pagesize=A4
            )

            page_width, page_height = A4
            y = page_height - 55


            def add_line(text, font_size=11, gap=22):
                global_y = None
                nonlocal_placeholder = None


            def write_text(text, font_size=11):
                nonlocal_dummy = None
                return text


            pdf.setTitle("Smart Solo Travel Budget Planner")

            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(45, y, "Smart Solo Travel Budget Planner")
            y -= 35

            pdf.setFont("Helvetica", 12)
            pdf.drawString(45, y, f"Destination: {destination}")
            y -= 22

            pdf.drawString(45, y, f"Starting city: {start_location}")
            y -= 22

            pdf.drawString(45, y, f"Trip duration: {days} days")
            y -= 22

            pdf.drawString(45, y, f"Travel style: {travel_style}")
            y -= 22

            pdf.drawString(45, y, f"Total budget: Rs. {budget:,.0f}")
            y -= 22

            pdf.drawString(45, y, f"Estimated total: Rs. {trip_cost:,.0f}")
            y -= 22

            pdf.drawString(45, y, f"Budget remaining: Rs. {remaining:,.0f}")
            y -= 35

            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(45, y, "Expense Breakdown")
            y -= 25

            pdf.setFont("Helvetica", 11)

            for _, row in expense_data.iterrows():
                if y < 65:
                    pdf.showPage()
                    y = page_height - 55
                    pdf.setFont("Helvetica", 11)

                pdf.drawString(
                    45,
                    y,
                    f"{row['Expense']}: Rs. {row['Estimated cost (₹)']:,.0f}"
                )
                y -= 20

            y -= 15
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(45, y, "Day-by-Day Itinerary")
            y -= 25

            pdf.setFont("Helvetica", 11)

            for day in range(1, int(days) + 1):

                if y < 85:
                    pdf.showPage()
                    y = page_height - 55
                    pdf.setFont("Helvetica", 11)

                place_index = (day - 1) % len(places)
                selected_place = places.iloc[place_index]

                pdf.drawString(
                    45,
                    y,
                    f"Day {day}: Visit {selected_place['place']}"
                )
                y -= 20

                pdf.drawString(
                    60,
                    y,
                    "Explore nearby attractions and enjoy local food."
                )
                y -= 28

            if y < 65:
                pdf.showPage()
                y = page_height - 55

            pdf.setFont("Helvetica-Oblique", 9)
            pdf.drawString(
                45,
                y,
                "Costs are estimates. Confirm actual fares and prices before travel."
            )

            pdf.save()

            pdf_buffer.seek(0)

            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_buffer.getvalue(),
                file_name="solo_travel_itinerary.pdf",
                mime="application/pdf"
            )
            # STEP 10: Interactive Travel Map

            st.divider()
            st.header("🗺️ Explore Your Destination on the Map")

            st.write(
                "View the sample locations available for your selected destination."
            )

            map_places = df[df["destination"] == destination].copy()

            if not map_places.empty:

                map_places = map_places.rename(
                    columns={
                        "latitude": "latitude",
                        "longitude": "longitude"
                    }
                )

                st.map(
                    map_places,
                    latitude="latitude",
                    longitude="longitude",
                    size=100
                )

                st.subheader("📍 Locations")

                for _, location in map_places.iterrows():
                    st.write(
                        f"**{location['place']}** — {location['category']}"
                    )

            else:
                st.info("No mapped locations are available for this destination.")