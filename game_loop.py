# import
import random
import os
import time

# グローバル変数
TRAP_DAMAGE = 10        # 沼のダメージ量
HEAL_AMOUNT = 75        # 薬草の回復量
PLAYER_MAX_HP = 150     # プレイヤーの最大HP
PLAYER_BASE_ATTACK = 20 # プレイヤーの素の攻撃力
PLAYER_BASE_DEFENSE = 5 # プレイヤーの素の防御力
SWORD_BONUS = 10        # 剣を装備した時の攻撃力ボーナス
SHIELD_BONUS = 5        # 盾を装備した時の防御力ボーナス
ARMOR_BONUS = 5         # 鎧を装備した時の防御力ボーナス

# 部屋を管理
class Room: # オバタ
    def __init__(self):
        self.has_enemy = None   # 部屋にいる敵
        self.has_item = None    # 部屋にあるアイテム
        self.is_swamp = False   # 沼かどうか
        self.is_castle = False  # 城かどうか
        self.visited = False    # プレイヤーが足を踏み入れたか

class Player: # イチカワ
    def __init__(self):
        self.now_x = 0
        self.now_y = 0
        self.hp = PLAYER_MAX_HP
        self.attack = PLAYER_BASE_ATTACK
        self.defence = PLAYER_BASE_DEFENSE
        self.sword_bool = False
        self.shielld_bool = False
        self.armor

class Enemy:
    def __init__(self, name, hp, strong_attack, weak_attack, pierce_attack):
        self.name = name
        self.hp = hp
        self.strong_attack = strong_attack
        self.weak_attack = weak_attack
        self.pierce_attack = pierce_attack

class Dragon(Enemy):
    def __init__(self):
        # 名前, HP, 強攻撃力, 弱攻撃力, 盾貫通攻撃力
        super().__init__("ドラゴン", 80, 40, 20, 30)

class Knight(Enemy):
    def __init__(self):
        # 名前, HP, 強攻撃力, 弱攻撃力, 盾貫通攻撃力
        super().__init__("あくまのきし", 120, 50, 30, 40)

class Ryuou(Enemy):
    def __init__(self):
        # 名前, HP, 強攻撃力, 弱攻撃力, 盾貫通攻撃力
        super().__init__("りゅうおう", 150, 60, 40, 50)

# マップの初期化 (敵、アイテム、沼、城 の配置)
def init_map(): # オバタ
    """
    マップイメージ
     0    1    2    3    4
    (城) (  ) (  ) (沼) (  ) 0
    (  ) (村) (  ) (  ) (ド) 1
    (沼) (  ) (剣) (  ) (  ) 2
    (あ) (  ) (  ) (沼) (沼) 3
    (  ) (盾) (廃) (沼) (り) 4
    """
    global map, enemies_list, enemies_defeated_count

    # 5x5のリストを全て新しいRoomインスタンスで初期化
    # (Y, X) の順で管理
    map = [[Room() for _ in range(5)] for _ in range(5)]
    # 敵リストを初期化
    enemies_list = [Dragon(), Knight(), Ryuou()]
    # 討伐数を初期化
    enemies_defeated_count = 0

    # 敵の配置
    map[1][4].has_enemy = enemies_list[0]  # (1, 4) に Dragon
    map[3][0].has_enemy = enemies_list[1]  # (3, 0) に Knight
    map[4][4].has_enemy = enemies_list[2]  # (4, 4) に Ryuou

    # アイテムの配置
    map[2][2].has_item = "sword"   # (2, 2) に 剣
    map[4][1].has_item = "shield"  # (4, 1) に 盾
    map[1][1].has_item = "herb"    # (1, 1) に 薬草

    # 沼の配置
    map[0][4].is_swamp = True
    map[2][0].is_swamp = True
    map[3][3].is_swamp = True
    map[3][4].is_swamp = True
    map[4][3].is_swamp = True

    # 城の配置
    map[0][0].is_castle = True

# マップとステータスを表示
def show_map(player): # オバタ
    print("--- マップ ---")
    px = player.now_x # プレイヤーのX座標
    py = player.now_y # プレイヤーのY座標

    #マップを表示
    for y in range(5):
        row_str = "" # 1行分の表示文字列を初期化
        for x in range(5):
            room = map[y][x] # (x, y) の部屋情報を取得
            is_adjacent = abs(x - px) + abs(y - py) == 1

            # 1. プレイヤーの現在地か？
            if px == x and py == y:
                row_str = row_str + " P " # プレイヤーを表示

            # 2. 訪問済みか？
            elif room.visited == True:
                if room.is_castle == True:
                    row_str = row_str + " C " # 訪問済みの城
                elif room.is_swamp == True:
                    row_str = row_str + " ~ " # 訪問済みの沼
                else:
                    row_str = row_str + " . " # 訪問済みの床

            # 3.隣接しているか？
            elif is_adjacent == True:
                if room.is_castle == True:
                    row_str = row_str + " C "
                elif room.has_enemy != None:
                    if isinstance(room.has_enemy, Dragon):
                        row_str = row_str + " ド "
                    elif isinstance(room.has_enemy, Knight):
                        row_str = row_str + " あ "
                    elif isinstance(room.has_enemy, Ryuou):
                        row_str = row_str + " り "
                elif room.is_swamp == True:
                    row_str = row_str + " ~ "
                elif room.has_item != None:
                    if room.has_item == "sword":
                        row_str = row_str + " 剣 "
                    elif room.has_item == "shield":
                        row_str = row_str + " 盾 "
                    elif room.has_item == "herb":
                         row_str = row_str + " 薬 "
                    else:
                         row_str = row_str + " . "
                else:
                    row_str = row_str + " . "

            # 4. 上記以外
            else:
                row_str = row_str + " ? " # 見えない

        print(row_str)

    # ステータス表示
    print("--- ステータス ---")
    print(f"HP: {player.hp}/{PLAYER_MAX_HP}")
    print(f"攻撃力: {player.attack} {'(剣)' if player.sword_bool else ''}")
    print(f"防御力: {player.defense} {'(盾)' if player.shield_bool else ''} {'(鎧)' if player.armor_bool else ''}")
    print(f"薬草: {player.number_of_herbs}")
    print("-----------------")

def show_rules(): # イワタ
    print("--- 勇者の冒険 ---")
    print("ダンジョンを探索し、3体の敵を倒して城(C)に戻れ。")
    print("\n--- マップ記号 ---")
    print(" P: 勇者 (現在地)")
    print(" ?: 未訪問・未隣接の部屋")
    print(" .: 床")
    print(" ~: 沼")
    print(" C: 城")
    print("\n--- 隣接マス表示 ---")
    print(" ド: ドラゴン")
    print(" あ: あくまのきし")
    print(" り: りゅうおう")
    print(" 剣: 剣")
    print(" 盾: 盾")
    print(" 薬: 薬草")
    print("\n--- 操作 ---")
    print("移動: 'w' (上), 'a' (左), 's' (下), 'd' (右) を入力して Enter")
    input("\n--- Enterキーでゲーム開始 ---")

def move_player(player): # モリヤ
    None

def get_item(player, item_name): # モリヤ
    None

def trap(player): # モリヤ
    None

def battle(player, enemy):
    # 保留
    None

def main(): # フジモト
    """
    初期化項目
    ・マップ（空マップとして、2次元リスト）
    ・勇者
    ・敵（3つ）

    初期動作

    ループ処理
    """


    #初期化
    init_map()
    player = Player()

main()