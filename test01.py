import random
import os
import time

TRAP_DAMAGE = 10        # 沼のダメージ量
HEAL_AMOUNT = 75        # 薬草の回復量
PLAYER_MAX_HP = 150     # プレイヤーの最大HP
PLAYER_BASE_ATTACK = 20 # プレイヤーの素の攻撃力
PLAYER_BASE_DEFENSE = 5 # プレイヤーの素の防御力
SWORD_BONUS = 10        # 剣を装備した時の攻撃力ボーナス
SHIELD_BONUS = 5        # 盾を装備した時の防御力ボーナス
ARMOR_BONUS = 5         # 鎧を装備した時の防御力ボーナス


class Room:
    """ ダンジョンの各部屋の状態を管理 """
    def __init__(self):
        self.has_enemy = None   # 部屋にいる敵
        self.has_item = None    # 部屋にあるアイテム
        self.is_swamp = False   # 沼かどうか
        self.is_castle = False  # 城かどうか
        self.visited = False    # プレイヤーが足を踏み入れたか

class Player:
    """ プレイヤー（勇者）の状態を管理 """
    def __init__(self):
        self.now_x = 0  # 勇者の現在地のx座標
        self.now_y = 0  # 勇者の現在地のy座標
        self.hp = PLAYER_MAX_HP  # プレイヤーのHP
        self.attack = PLAYER_BASE_ATTACK  # プレイヤーの 攻撃力
        self.defense = PLAYER_BASE_DEFENSE # プレイヤーの防御力
        self.sword_bool = False  # 剣の所持の有無
        self.shield_bool = False # 盾の所持の有無
        self.armor_bool = False  # 鎧の所持の有無
        self.number_of_herbs = 0 # 薬草の所持数
        self.is_defending = False # このターン、防御を選んだか

    def update_stats(self):
        """ 
        装備の状況（剣、盾、鎧）に合わせて
        self.attack と self.defense の変数を再計算し、更新。
        """
        
        # 1. 攻撃力の計算
        self.attack = PLAYER_BASE_ATTACK
        if self.sword_bool == True:
            self.attack = self.attack + SWORD_BONUS
        
        # 2. 防御力の計算
        self.defense = PLAYER_BASE_DEFENSE
        if self.shield_bool == True:
            self.defense = self.defense + SHIELD_BONUS
        
        if self.armor_bool == True:
            self.defense = self.defense + ARMOR_BONUS
        
        print("ステータスが更新されました。")

    def heal(self):
        """ HPを回復 """
        self.hp = self.hp + HEAL_AMOUNT # HPを回復
        
        # 最大HPを超えないように調整
        if self.hp > PLAYER_MAX_HP:
            self.hp = PLAYER_MAX_HP # 最大HPでストップ
            
        print(f"薬草を使った。HPが{HEAL_AMOUNT}回復した。 (現在HP: {self.hp})")

    def take_damage(self, actual_damage):
        """ ダメージ計算済みの値を受け取り、HPを減らす """
        self.hp = self.hp - actual_damage
        print(f"(残りHP: {self.hp})")
        
        # 死亡判定 (HPが0以下か)
        if self.hp <= 0:
            return True
        else:
            return False

class Enemy:
    """ 敵の基底クラス"""
    def __init__(self, name, hp, strong_attack, weak_attack, penetrate_attack):
        self.name = name                # 敵の名前
        self.hp = hp                    # 敵のHP
        self.strong_attack = strong_attack # 敵の強攻撃力
        self.weak_attack = weak_attack     # 敵の弱攻撃力
        self.penetrate_attack = penetrate_attack # 盾貫通攻撃力
        self.can_act = True             # 行動できるか
        self.is_charging = False        # 現在「タメ」中か

    def perform_attack(self, player):
        """ 
        敵の行動を処理
        player オブジェクトを受け取り、その状態を確認
        """
        
        # 1. スタン判定
        if self.can_act == False:
            print(f"{self.name}はスタンしていて動けない！")
            self.can_act = True
            return False

        damage = 0
        defense_value = 0
        is_dead = False
        
        # 2. タメ後の行動
        if self.is_charging == True:
            
            self.is_charging = False # タメ状態を解除
            
            #「強攻撃」か「盾貫通攻撃」
            action = random.choice(['strong', 'penetrate'])
            
            if action == 'strong':
                # --- 強攻撃 ---
                print(f"{self.name}の強攻撃！")
                damage = self.strong_attack
                
                if player.armor_bool == True:
                    defense_value = 20
                else:
                    defense_value = 10
                
                if player.is_defending == True:
                    #プレイヤーが防御していた場合
                    print("勇者は防御している！")
                    print("盾と鎧でダメージを大きく軽減した！")
                    
                    #強攻撃を防御した場合、敵がスタン
                    self.can_act = False
                

            elif action == 'penetrate':
                # --- 盾貫通攻撃 ---
                print(f"{self.name}の盾貫通攻撃！")
                damage = self.penetrate_attack
                
                if player.armor_bool == True:
                    defense_value = 10
                else:
                    defense_value = 5
                    
                if player.is_defending == True:
                    print("勇者は防御している！ しかし盾を貫通された！")
        
        # 3. 通常時の行動 (タメていない場合)
        else:
            #「通常攻撃」 か 「タメ行動」
            action = random.choice(['weak', 'charge'])
            
            if action == 'weak':
                # --- 通常攻撃 ---
                print(f"{self.name}の通常攻撃！")
                damage = self.weak_attack
                
                if player.armor_bool == True:
                    defense_value = 20
                else:
                    defense_value = 10
                
                if player.is_defending == True:
                    print("勇者は防御している！")
                
            
            elif action == 'charge':
                # --- タメ行動 ---
                print(f"{self.name}は力をためている...")
                self.is_charging = True
        
        # 4. ダメージ計算と実行
        if damage > 0:
            actual_damage = max(0, damage - defense_value)
            
            print(f"勇者は {actual_damage} のダメージを受けた！")
            is_dead = player.take_damage(actual_damage)
            
        elif self.is_charging == True:
            pass
        else:
            # 一応
            print(f"{self.name}の攻撃はミスになった。")

        return is_dead

# --- 敵クラス ---
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


dungeon_map = [[Room() for _ in range(5)] for _ in range(5)]
enemies_list = [Dragon(), Knight(), Ryuou()] 
enemies_defeated_count = 0 

# --- 関数定義 ---

#なくてもいい
def clear_screen():
    """ ターミナル画面をクリア"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

#なくてもいい
def wait(seconds=1):
    """ 指定秒数待機（ゲームのテンポ調整用） """
    time.sleep(seconds)

def init_map():
    """ 
    マップの初期化 (敵、アイテム、沼、城 の配置)
    """
    global dungeon_map, enemies_list, enemies_defeated_count
    
    # 5x5マップを全て新しいRoomオブジェクトで埋め直す
    dungeon_map = [[Room() for _ in range(5)] for _ in range(5)]
    # 敵リストも新しく作り直す
    enemies_list = [Dragon(), Knight(), Ryuou()]
    # 討伐数リセット
    enemies_defeated_count = 0
    
    # (Y, X) の順で指定
    
    # 敵の配置
    dungeon_map[1][4].has_enemy = enemies_list[0]  # (1, 4) に Dragon
    dungeon_map[3][0].has_enemy = enemies_list[1]  # (3, 0) に Knight
    dungeon_map[4][4].has_enemy = enemies_list[2]  # (4, 4) に Ryuou
    
    # アイテムの配置
    dungeon_map[2][2].has_item = "sword"   # (2, 2) に 剣
    dungeon_map[4][1].has_item = "shield"  # (4, 1) に 盾
    dungeon_map[1][1].has_item = "herb"    # (1, 1) に 薬草
    
    # 沼の配置
    dungeon_map[0][4].is_swamp = True
    dungeon_map[2][0].is_swamp = True
    dungeon_map[3][3].is_swamp = True
    dungeon_map[3][4].is_swamp = True
    dungeon_map[4][3].is_swamp = True
    
    # 城の配置
    dungeon_map[0][0].is_castle = True

def show_rule():
    """ ゲームのルールを表示 """
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

def show_map(player):
    """ 
    マップとステータスを表示
    """
    print("--- マップ ---")
    px = player.now_x # プレイヤーのX座標
    py = player.now_y # プレイヤーのY座標
    
    #マップを表示
    for y in range(5):
        row_str = ""
        for x in range(5):
            room = dungeon_map[y][x] # (x, y) の部屋情報を取得
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

def move_player(player):
    """ プレイヤーの移動処理"""
    while True:
        move = input("移動 (w/a/s/d): ").lower().strip()
        dx = 0 # X方向の移動量
        dy = 0 # Y方向の移動量
        
        if move == 'w':
            dy = -1 # 上へ
        elif move == 'a':
            dx = -1 # 左へ
        elif move == 's':
            dy = 1  # 下へ
        elif move == 'd':
            dx = 1  # 右へ
        else:
            print("w, a, s, d のいずれかを入力してください。")
            continue
            
        # 移動先の座標
        new_x = player.now_x + dx
        new_y = player.now_y + dy
        
        # マップの範囲内かチェック
        if 0 <= new_x < 5 and 0 <= new_y < 5:
            # 範囲内なら、プレイヤーの座標を更新
            player.now_x = new_x
            player.now_y = new_y
            break
        else:
            print("その方向には移動できない。")

def get_item(player, item_name):
    """ アイテム取得処理 """
    print(f"アイテムを見つけた！")
    wait(1)
    
    if item_name == "sword":
        player.sword_bool = True
        print("剣を装備した！攻撃力が上がった。")
        player.update_stats()
        
    elif item_name == "shield":
        player.shield_bool = True
        print("盾を装備した！防御力が上がった。")
        player.update_stats()
        
    elif item_name == "herb":
        player.number_of_herbs = player.number_of_herbs + 3
        print("薬草を3個拾った。")

def trap(player):
    """ 沼を踏んだ時の処理 """
    print("沼地に入ってしまった！")
    wait(1)

    if player.armor_bool == True:
        print("しかし、鎧が沼のダメージを防いだ！")
    
    else:
        print(f"勇者は {TRAP_DAMAGE} のダメージを受けた！")
        player.hp = player.hp - TRAP_DAMAGE
        if player.hp <= 0:
            return True
            
    return False

def battle(player, enemy):
    """ 
    戦闘処理
    順序: 1. プレイヤー選択 -> 2. 敵の行動 -> 3. プレイヤー行動実行
    """
    global enemies_defeated_count
    print(f"--- {enemy.name} が現れた！ ---")
    wait(1)

    # 戦闘開始時に敵の状態をリセット
    enemy.can_act = True
    enemy.is_charging = False

    # 戦闘ループ
    while player.hp > 0 and enemy.hp > 0:
        clear_screen()
        print(f"--- {enemy.name} (HP: {enemy.hp}) ---")
        print(f"--- 勇者 (HP: {player.hp}, 薬草: {player.number_of_herbs}) ---")
        
        # 敵の状態を表示
        if enemy.can_act == False:
            status_text = "スタン中"
        elif enemy.is_charging == True:
            status_text = "タメ中"
        else:
            status_text = "通常"
        print(f"敵の状態: {status_text}")
        
        print("-----------------")
        
        # 1. 勇者の行動選択
        player.is_defending = False
        
        print("\n勇者のターン！")
        player_action_choice = None # '1'(攻撃), '2'(防御), '3'(回復)
        
        while True:
            action = input("行動を選択 (1:攻撃, 2:防御, 3:回復): ").strip()
            
            if action == '1': # 攻撃
                player_action_choice = '1'
                break
                
            elif action == '2': # 防御
                if player.shield_bool == True:
                    player.is_defending = True
                    player_action_choice = '2'
                    print("勇者は盾を構えて防御している！")
                    break
                else:
                    print("盾がないため防御できない！")
                    
            elif action == '3': # 回復
                if player.number_of_herbs > 0:
                    player_action_choice = '3'
                    break
                else:
                    print("薬草を持っていない！")

            else:
                print("1, 2, 3 のいずれかを入力してください。")
        
        wait(1)

        # 2. 敵の行動
        player_dead = enemy.perform_attack(player) 
        
        if player_dead == True:
            print("勇者は倒れてしまった...")
            return False  # 戦闘敗北

        wait(2)

        # 3. 勇者の行動実行
        if player_action_choice == '1':
            damage = player.attack
            enemy.hp = enemy.hp - damage
            print(f"勇者の攻撃！ {enemy.name} に {damage} のダメージを与えた！")
        
        elif player_action_choice == '3':
            player.heal()
            player.number_of_herbs = player.number_of_herbs - 1
        
        elif player_action_choice == '2':
            pass
        
        wait(2)

        # 4. 敵のHP判定
        if enemy.hp <= 0:
            print(f"\n{enemy.name} を倒した！")
            
            # 倒した敵に応じたテキストと処理
            if isinstance(enemy, Dragon):
                print("「ドラゴンのテキスト」 (ドラゴンを倒した！) ")
            elif isinstance(enemy, Knight):
                print("「あくまのきしのテキスト」 (あくまのきしを倒した！) ")
                #鎧入手の判定
                if player.armor_bool == False:
                    player.armor_bool = True
                    print("鎧を手に入れた！これで沼は怖くない。")
                    player.update_stats()
            elif isinstance(enemy, Ryuou):
                print("「りゅうおうのテキスト」 (りゅうおうを倒した！) ")
            
            enemies_defeated_count = enemies_defeated_count + 1
            return True  # 戦闘勝利

        wait(2)
        
    return False


def main():
    # 1. 初期化
    init_map()
    player = Player()
    player.now_x = 0
    player.now_y = 0
    player.update_stats()   
    win_bool = False
    defeat_bool = False

    # 2. ルール表示
    clear_screen()
    show_rule()
    
    # 3. メインループ
    while win_bool == False and defeat_bool == False:
        clear_screen()
        
        # 3a. マップ表示
        show_map(player)        
        # 現在プレイヤーがいる部屋の情報を取得
        current_room = dungeon_map[player.now_y][player.now_x]
        
        event_occurred = False 
        
        # 3b. 訪問処理
        is_first_visit = False
        if current_room.visited == False:
             is_first_visit = True
             current_room.visited = True
             if not current_room.is_castle:
                 print("この部屋には初めて入った。")
                 wait(1)
                 event_occurred = True

        # 3c. 敵判定
        if current_room.has_enemy != None:
            event_occurred = True 
            battle_result = battle(player, current_room.has_enemy)
            
            if battle_result == True:
                current_room.has_enemy = None
                print(f"残り敵数: {len(enemies_list) - enemies_defeated_count} 体")
                wait(3)
            else:
                defeat_bool = True
                print("ゲームオーバー...")
                break
        
        # 3d. アイテム判定
        if is_first_visit == True and current_room.has_enemy == None and current_room.has_item != None:
            event_occurred = True 
            get_item(player, current_room.has_item)
            current_room.has_item = None
            wait(2)

        # 3e. 沼判定
        if current_room.has_enemy == None and current_room.is_swamp == True:
            event_occurred = True 
            is_dead = trap(player)
            if is_dead == True:
                defeat_bool = True
                print("勇者は沼に沈んでしまった...")
                print("ゲームオーバー...")
                break
            wait(2)
            
        # 3f. 城判定
        if current_room.is_castle == True:
            if enemies_defeated_count == len(enemies_list):
                win_bool = True
                clear_screen()
                print("*********************************")
                print("すべての敵を倒し、城に戻った！")
                print("おめ！")
                print("*********************************")
                break
            else:
                # 最初の訪問時以外（戻ってきた場合）
                if is_first_visit == False:
                    print(f"まだ {len(enemies_list) - enemies_defeated_count} 体の敵が残っている...")
                    print("すべての敵を倒してから戻ってこよう。")
                    wait(3)
                    event_occurred = True 

        # 3g. 移動
        if win_bool == False and defeat_bool == False:
            
            if event_occurred == True:
                clear_screen()
                show_map(player)
            
            move_player(player)

    # 4. ゲーム終了
    print("\n--- ゲーム終了 ---")


if __name__ == "__main__":
    main()