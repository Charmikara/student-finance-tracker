def normalize_category(category: str) -> str:
    if not isinstance(category, str):
        raise TypeError("Category must be a string.")

    normalized_category = category.strip().lower()
    if not normalized_category:
        raise ValueError("Category cannot be empty.")

    return normalized_category
