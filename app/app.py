import streamlit as st

from recommendation_engine import RecommendationEngine

# Category-Subcategory mapping
CATEGORY_MAP = {
    "BEER": [
        "ALE",
        "DRY STOUT",
        "HARD SELTZER",
        "VARIETY PACK",
        "STOUT - IMPERIAL FLAVORED",
        "CRAFT & SEASONAL BEER",
        "BELGIAN BEERS",
        "BOCK - DUNKLER BOCK",
        "HARD & SPIKED",
        "FLAVORED BEER",
        "DOUBLE IPA",
        "MALT LIQUOR",
        "STOUT",
        "ISA - SESSION IPA",
        "STOUT - IMPERIAL",
        "HARD SODA",
        "IIPA - IMPERIAL / DOUBLE IPA",
        "SMOKED - RAUCHBIER",
        "SOUR / WILD BEER",
        "FLAVORED - FRUIT",
        "IIPA DIPA - IMPERIAL / DOUBLE IPA",
        "RADLER / SHANDY",
        "NON ALC",
        "DUBBEL",
        "IPA - WHITE",
        "IPA - HAZY / NEIPA",
        "BITTER - PREMIUM / STRONG / ESB",
        "IPA",
        "PORTER - FLAVORED",
        "LAGER",
        "IPA - ENGLISH",
        "FLAVORED",
        "STOUT - MILK / SWEET",
        "BERLINER WEISSE - FLAVORED",
        "IPA - FLAVORED",
        "ISA",
        "WEISSBIER - HEFEWEIZEN",
        "SPECIALTY GRAIN - OTHER",
        "SESSION IPA",
        "BOCK - DOPPELBOCK",
        "PILSNER",
        "IMPERIAL IPA",
        "TRIPEL",
        "PILSENER - CZECH / SVETLÝ",
        "CALIFORNIA COMMON / STEAM BEER",
        "SAISON / FARMHOUSE / GRISETTE"
    ],
    "LIQUOR": [
        "PISCO",
        "IRISH WHISKEY",
        "PREMADE COCKTAIL",
        "MARGARITA READY-TO-DRINK",
        "WHISKY",
        "CACHACA",
        "APERITIVO",
        "FORTIFIED WINE",
        "BITTERS",
        "VODKA",
        "GRAPPA",
        "COGNAC",
        "SHOCHU",
        "MALT LIQUOR",
        "LIQUOR",
        "AMERICAN WHISKEY",
        "WHISKEY",
        "RUM",
        "BOURBON",
        "GRAIN ALCOHOL",
        "APERITIF",
        "BRANDY/COGNAC",
        "JAPANESE WHISKY",
        "WHISKEY - IRISH",
        "CANADIAN WHISKY",
        "GIN",
        "LIQUEUR CORDIALS & SCHNAPPS",
        "WHISKY - CANADIAN",
        "WHISKY - JAPANESE",
        "MIXER",
        "VERMOUTH",
        "MEZCAL",
        "SOJU",
        "SCOTCH",
        "TEQUILA",
        "PREPARED COCKTAIL",
        "WHISKY - REST OF WORLD",
        "BRANDY",
        "WHISKEY - AMERICAN"
    ],
    "WINE": [
        "FORTIFIED",
        "CHAMPAGNE & SPARKLING WINE",
        "FORTIFIED WINE",
        "CHAMPAGNE",
        "CHAMPAGNE & SPARKLING",
        "ROSÉ WINE",
        "RED WINE",
        "SAKE",
        "PORT WINE",
        "SPARKLING SAKE",
        "WINE MISCELLANEOUS",
        "ROSE & BLUSH",
        "SPARKLING WINE",
        "NO & LOW WINE",
        "WHITE WINE",
        "DESSERT & FORTIFIED",
        "PLUM WINE",
        "ORANGE WINE",
        "SAUV BLANC",
        "ROSE WINE"
    ]
}


def display_simple_json(data):
    st.header("Recommendation Results")

    print(data['data'])
    for item in data['data']:
        st.subheader(f"🍷 {item['category']}")
        st.markdown(f"""
        **Total Units:** {item['total_units']}  
        **Cost per Unit:** ${item['per_unit_cost']}  
        **Total Cost:** ${item['total_units'] * item['per_unit_cost']:,}

        **Subcategories:**
        """)

        for subcat, units in item['subcategories'].items():
            st.markdown(f"- {subcat}: {units} units")

        st.markdown("---")


def main():
    st.title("Beverage Recommendation System")

    # Initialize the recommendation engine
    engine = RecommendationEngine()

    # Create input sections
    st.header("Event Details")

    # Number of attendees input
    num_attendees = st.number_input(
        "Number of Attendees",
        min_value=1,
        max_value=1000,
        value=50
    )

    # Budget per person input
    budget_per_person = st.number_input(
        "Budget per Person ($)",
        min_value=1,
        max_value=1000,
        value=20
    )

    # Category selection
    st.header("Beverage Categories")

    # Dictionary to store selected options
    selected_categories = {}

    # Create expandable sections for each main category
    for category, subcategories in CATEGORY_MAP.items():
        with st.expander(f"{category} Options", expanded=True):
            st.write(f"Select {category} types:")

            # Create columns for better organization
            cols = st.columns(3)
            selected_subcats = []

            # Create checkboxes for subcategories
            for i, subcat in enumerate(subcategories):
                col_idx = i % 3
                with cols[col_idx]:
                    if st.checkbox(subcat, key=f"{category}_{subcat}"):
                        selected_subcats.append(subcat)

            if selected_subcats:
                selected_categories[category] = selected_subcats

    # Calculate button
    if st.button("Generate Recommendations"):
        if not selected_categories:
            st.warning("Please select at least one beverage type")
        else:
            try:
                # Get recommendations
                results = engine.calculate_total_drinks(
                    num_attendees,
                    budget_per_person,
                    selected_categories
                )

                # Display results
                display_simple_json(results)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Add help section
    with st.expander("Help"):
        st.markdown("""
        **How to use this tool:**
        1. Enter the number of attendees
        2. Set your budget per person
        3. Select the types of beverages you want to include
        4. Click 'Generate Recommendations' to see the results
        """)


if __name__ == "__main__":
    main()
