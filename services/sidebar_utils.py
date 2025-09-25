def normalize_city_name_for_storage(city_name):
    # 全て小文字に変換
    normalized_name = city_name.lower()

    # 特定の接尾辞を除去
    suffixes_to_remove = ["市", "県", "都", "府", "郡", "町", "村"]
    for suffix in suffixes_to_remove:
        if normalized_name.endswith(suffix):
            normalized_name = normalized_name[:-len(suffix)]
            break # 一致する最初の接尾辞を除去したら終了

    # その他の一般的な表記揺れを吸収（例: スペース除去など、必要に応じて追加）
    normalized_name = normalized_name.replace(" ", "")

    return normalized_name
