from typing import List, Tuple

from repositories.animal_shelter_repository import get_animal_shelter, get_data_source_label
from services.sort_service import SORT_FUNCTIONS, time_record_sort


class DashboardService:
    def __init__(self):
        self.animal_shelter = get_animal_shelter()
        self.data_source_label = get_data_source_label(self.animal_shelter)

    def get_initial_dataframe(self, filter_type: str = "RESET"):
        return self.animal_shelter.get_dashboard_data(filter_type)

    def get_sorted_records(
        self,
        filter_type: str,
        sort_column: str,
        sort_algorithm: str,
        sort_order: str,
    ) -> Tuple[List[dict], str]:
        data = self.animal_shelter.get_dashboard_data(filter_type)
        records = data.to_dict("records")

        if not records or not sort_column:
            return records, "No rows available to sort."

        reverse_sort = sort_order == "desc"
        sort_label, sort_function, complexity = SORT_FUNCTIONS.get(sort_algorithm, SORT_FUNCTIONS["quick"])
        displayed_records, elapsed_time = time_record_sort(sort_function, records, sort_column, reverse_sort)
        timing_message = (
            f"{sort_label}: {elapsed_time:.6f} seconds | "
            f"Time Complexity: {complexity} | "
            f"Displaying results by '{sort_column}' ({'descending' if reverse_sort else 'ascending'})."
        )
        return displayed_records, timing_message
