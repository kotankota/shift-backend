# from dotenv import load_dotenv
# import os
# from openai import OpenAI
# from app.crud.item import crud_item
# from app.crud.user_disaster_prevention_info import crud_user_disaster_prevention_info
# from sqlalchemy.orm import Session
# import json
# from app.schemas.item import ProposedDisasterGoodsCreate, ProposedDisasterGoods, UserChatRequest
# from app.crud.proposed_disaster_goods import crud_proposed_disaster_goods

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI(
#     api_key=api_key
# )

# def get_disaster_items_for_family(user_id: int, db: Session):
#     user_disaster_prevention_info = crud_user_disaster_prevention_info.get_by_user_id(db=db, user_id=user_id)
#     family_members = user_disaster_prevention_info.family_members
#     print(family_members)
#     if not family_members:
#         return "No family members found."

#     disaster_items = crud_item.list(db=db)
#     family_info_str = json.dumps(family_members, ensure_ascii=False, indent=2)
#     items_str = json.dumps(
#         [{"id": item.id, "name": item.name, "description": item.description, "category": item.category} for item in disaster_items],
#         ensure_ascii=False, indent=2
#     )

#     prompt = (
#         f"以下は家族構成の情報です:\n{family_info_str}\n\n"
#         f"そして、以下は防災グッズのリストです（各グッズのID、名前、説明、カテゴリー）:\n{items_str}\n\n"
#         "この家族に最適な防災グッズの提案を、以下の形式でJSONで返答してください:\n"
#         "{\n"
#         "  \"proposed_items\": [\n"
#         "    {\n"
#         "      \"item_id\": 整数,\n"
#         "      \"priority_level\": 整数,\n"
#         "      \"quantity\": 整数\n"
#         "    }\n"
#         "  ]\n"
#         "}\n"
#         "item_idは防災グッズリストからのID、priority_levelは1から5までの緊急度(1が緊急度高い)、quantityは提案される数量です。"
#     )
#     print(prompt)

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             response_format={"type": "json_object"},
#             messages=[
#                 {"role": "system", "content": "JSON形式で返答してください"},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=4096
#         )
        
#         proposed_items = json.loads(response.choices[0].message.content)
#         print(proposed_items)

#         if not isinstance(proposed_items, dict) or 'proposed_items' not in proposed_items:
#             raise ValueError("Unexpected response format from OpenAI API")

#         crud_proposed_disaster_goods.delete_by_user_id(db=db, user_id=user_id)

#         for item in proposed_items['proposed_items']:
#             item_id = item['item_id']
#             priority_level = item['priority_level']
#             quantity = item['quantity']
#             proposed_disaster_good = ProposedDisasterGoodsCreate(
#                 item_id=item_id,
#                 priority_level=priority_level,
#                 quantity=quantity
#             )
#             crud_proposed_disaster_goods.create_with_user_id(db=db, obj_in=proposed_disaster_good, user_id=user_id)

#         return crud_proposed_disaster_goods.list_by_user_id(db=db, user_id=user_id)

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return f"An error occurred: {str(e)}"

# # 前のに戻してとかは厳しいね

# def update_disaster_items_with_user_input(user_id: int, user_request: UserChatRequest, db: Session):
#     # 現在の提案リストを取得
#     user_disaster_prevention_info = crud_user_disaster_prevention_info.get_by_user_id(db=db, user_id=user_id)
#     family_members = user_disaster_prevention_info.family_members
#     if not family_members:
#         return "No family members found."
#     family_info_str = json.dumps(family_members, ensure_ascii=False, indent=2)
#     current_goods = crud_proposed_disaster_goods.list_by_user_id(db=db, user_id=user_id)
#     current_goods_list = [
#         {
#             "item_id": good.item_id,
#             "priority_level": good.priority_level,
#             "quantity": good.quantity,
#             "item": {
#                 "name": good.item.name,
#                 "description": good.item.description,
#                 "category": good.item.category,
#                 "image_url": good.item.image_url
#             }
#         } for good in current_goods
#     ]
    
#     # JSON形式でリスト化
#     current_goods_str = json.dumps(current_goods_list, ensure_ascii=False, indent=2)
#     user_request_str = user_request.request  # ここでUserChatRequestのrequest属性を直接使用する

#     # プロンプトの作成
#     prompt = (
#         f"以下は家族構成の情報です:\n{family_info_str}\n\n"
#         f"そして以下は現在の提案されている防災グッズリストです:\n{current_goods_str}\n\n"
#         f"以下はユーザーからの要求です:\n{user_request_str}\n\n"
#         "これらを基に、新しい提案グッズリストを生成してください。また、ユーザーの要求に基づいて行った変更点についてもコメントしてください(コメントにitem_idなどの情報は入れないでください)。以下の形式でJSONで返答してください:\n"
#         "{\n"
#         "  \"proposed_items\": [\n"
#         "    {\n"
#         "      \"item_id\": 整数,\n"
#         "      \"priority_level\": 整数,\n"
#         "      \"quantity\": 整数\n"
#         "    }\n"
#         "  ]\n"
#         "  \"comments\": \"変更内容に関するコメント\"\n"
#         "}\n"
#         "item_idは防災グッズリストからのID、priority_levelは1から5までの緊急度、quantityは提案される数量です。"
#     )

#     print(prompt)

#     try:
#         # GPT-4 API呼び出し
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             response_format={"type": "json_object"},
#             messages=[
#                 {"role": "system", "content": "JSON形式で返答してください"},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=4096
#         )
        
#         # GPT-4からの新しい提案リストとコメントを取得
#         result = json.loads(response.choices[0].message.content)
#         print(result)

#         if not isinstance(result, dict) or 'proposed_items' not in result or 'comments' not in result:
#             raise ValueError("Unexpected response format from OpenAI API")

#         # 現在の提案リストを削除し、更新されたリストで再生成
#         crud_proposed_disaster_goods.delete_by_user_id(db=db, user_id=user_id)

#         for item in result['proposed_items']:
#             item_id = item['item_id']
#             priority_level = item['priority_level']
#             quantity = item['quantity']
#             proposed_disaster_good = ProposedDisasterGoodsCreate(
#                 item_id=item_id,
#                 priority_level=priority_level,
#                 quantity=quantity
#             )
#             crud_proposed_disaster_goods.create_with_user_id(db=db, obj_in=proposed_disaster_good, user_id=user_id)

#         return {
#             "proposed_items": crud_proposed_disaster_goods.list_by_user_id(db=db, user_id=user_id),
#             "comments": result['comments']
#         }

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return f"An error occurred: {str(e)}"
