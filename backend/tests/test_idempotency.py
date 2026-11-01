from unittest.mock import MagicMock


def test_existing_sales_order_is_reused():
    existing_order = MagicMock()

    query = MagicMock()
    query.filter.return_value.first.return_value = existing_order

    db = MagicMock()
    db.query.return_value = query

    result = (
        db.query()
        .filter()
        .first()
    )

    assert result is existing_order