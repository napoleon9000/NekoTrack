def profit_estimation(data, toys_payout_rate=1/7.0, avg_toys_cost=2.5, fixed_cost=400):
    price_to_token_mapping = {
        10: 12,
        20: 26, 
        30: 42,
        50: 75,
        100: 150,
    }

    actual_data = []

    for value in data:
        if value in price_to_token_mapping:
            actual_data.append(price_to_token_mapping[value])
        else:
            actual_data.append(value)

    total_tokens = sum(actual_data)
    total_income = sum(data)
    print(f'Tokens payout: {total_tokens}')

    toys_payout = total_tokens * toys_payout_rate
    print(f'Avg. toys payout: {toys_payout}')

    profit = total_income - (toys_payout * avg_toys_cost) - fixed_cost
    print(f'profit: {profit}')

    return profit, total_income, total_tokens, toys_payout


def profit_estimation_with_total_payout(data, total_toys_payout, avg_toys_cost=2.5, fixed_cost=400):
    total_tokens = sum(data)
    total_income = sum(data)
    print(f'Tokens payout: {total_tokens}')

    toys_payout = total_toys_payout
    print(f'Avg. toys payout: {toys_payout}')

    profit = total_income - (toys_payout * avg_toys_cost) - fixed_cost
    print(f'profit: {profit}')
    total_tokens = sum(data)

    return profit, total_income, total_tokens, toys_payout
