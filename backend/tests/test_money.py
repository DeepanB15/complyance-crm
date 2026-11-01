from decimal import Decimal


def test_milestone_percentages():
    milestones = [
        Decimal("50"),
        Decimal("30"),
        Decimal("20"),
    ]

    assert sum(milestones) == Decimal("100")


def test_milestone_amounts():
    amount = Decimal("120000")

    amounts = [
        (amount * Decimal("50") / Decimal("100")).quantize(Decimal("0.01")),
        (amount * Decimal("30") / Decimal("100")).quantize(Decimal("0.01")),
        (amount * Decimal("20") / Decimal("100")).quantize(Decimal("0.01")),
    ]

    assert amounts == [
        Decimal("60000.00"),
        Decimal("36000.00"),
        Decimal("24000.00"),
    ]

    assert sum(amounts) == amount