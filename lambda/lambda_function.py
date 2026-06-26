import json
from pathlib import Path

import boto3 # AWSが公式に提供しているPython用のSDK。プログラムやスクリプトからあらゆるAWSサービスを構築・操作・自動化できる。
from boto3.dynamodb.conditions import Key # 条件式（Key）をシンプルに書くために追加

BASE_DIR = Path(__file__).resolve().parent
MAPPING_FILE = BASE_DIR / 'mappin.json'
_mapping_cache = None


def load_mapping():
    global _mapping_cache
    if _mapping_cache is None:
        with MAPPING_FILE.open('r', encoding='utf-8') as f:
            _mapping_cache = json.load(f)
    return _mapping_cache


# 自動デプロイテスト用追加OK

def lambda_handler(event, context):
    # `mappin.json` を読み込み
    mapping = load_mapping()
    print('--- mapping.json を読み込みました ---')
    print(mapping)

    # DynamoDBクライアントを作成
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('masumi-regional_weather_table_sort')
    
    # --- 1. 全件取得 (scan) ---
    responseall = table.scan()
    print('--- レスポンスを出力(scan) ---')
    print(responseall)
    
    # --- 2. 単一のデータを取り出す (get_item) ---
    response_get_item = table.get_item( 
        Key={
            'area_id': 'Tokyo',
            'created_at': 202606231100  # 【修正】ダブルクォーテーションを外し、数値（Int）にする
        }
    )
    print('--- レスポンスを出力(get_item) ---')
    print(response_get_item)

    # --- 3. ソートキーを使って範囲検索する (query) ---
    response_query = table.query( 
        # 【修正】パーティションキーの指定を追加し、{} を外す
        KeyConditionExpression=Key('area_id').eq('Tokyo') & Key('created_at').between(202606240000, 202606242359)
    )
    print('--- レスポンスを出力(query) ---')
    print(response_query)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }