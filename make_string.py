from datetime import datetime, timedelta


# Function to read JSON and create the output string for a given date
def read_json_create_output(json_data, date, output_string=""):
    try:
        # Find the entry for the given date
        current_data = None
        for entry in json_data.get("tagesplan", []):
            if entry.get("datum") == date:
                current_data = entry
                break

        # If there's no data for the current date or the cafeteria is closed, we skip this day
        if not current_data or "geschlossen" in current_data.get("text", ""):
            return output_string

        # Append date to the output string
        output_string += f"\n{date}:\n"

        # Process each category (meal type)
        for category in current_data.get("linie", []):
            category_name = category.get("ausgabe", "Unknown")
            output_string += f"{category_name}:\n"
            # Process each meal in the category
            for meal in category.get("gericht", []):
                # Prefer English meal name if available
                meal_name = meal.get("text_en", meal.get("text", "Unknown meal"))
                output_string += f"- {meal_name}\n"
        return output_string
    except Exception as e:
        return str(e)


# Function to get menu for the week starting from the current day
def get_menu_for_week(json_meal):
    try:
        output_string = ""
        current_date = datetime.now()
        for i in range(7):  # for the next 7 days including today
            date_str = current_date.strftime("%d.%m.%Y")
            output_string = read_json_create_output(json_meal, date_str, output_string)
            current_date += timedelta(days=1)  # move to the next day
        return output_string
    except Exception as e:
        return str(e)

