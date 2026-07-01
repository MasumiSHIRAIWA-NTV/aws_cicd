import json
import time
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
    # DynamoDBクライアントを作成
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('masumi-regional_weather_table_sort')
    
    # --- get_itemとqueryを500回実行 ---
    processing_times = []
    
    for i in range(500):
        start_time = time.time()
        
        # --- 1. 単一のデータを取り出す (get_item) ---
        response_get_item = table.get_item( 
            Key={
                'area_id': 'Tokyo',
                'created_at': 202606231100
            }
        )
        
        # --- 2. ソートキーを使って範囲検索する (query) ---
        response_query = table.query( 
            KeyConditionExpression=Key('area_id').eq('Tokyo') & Key('created_at').between(202606240000, 202606242359)
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        processing_times.append(elapsed_time)
        
        print(f'--- 処理 {i+1}: {elapsed_time:.6f}秒 ---')
    
    # --- 平均処理秒数を計算して出力 ---
    average_time = sum(processing_times) / len(processing_times)
    print(f'\n=== 平均処理秒数: {average_time:.6f}秒 ===')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Average processing time: {average_time:.6f} seconds')
    }