# Import pyxel module
import pyxel

# 定数の定義
SCREEN_WIDTH = 160  # 画面の幅
SCREEN_HEIGHT = 120  # 画面の高さ
PLAYER_SIZE = 8  # プレイヤーのサイズ
BULLET_SPEED = 3  # 弾の移動速度
PLAYER_SPEED = 2  # プレイヤーの移動速度

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2  # プレイヤーの初期位置X
        self.y = SCREEN_HEIGHT // 2  # プレイヤーの初期位置Y
        self.width = PLAYER_SIZE  # プレイヤーの幅
        self.height = PLAYER_SIZE  # プレイヤーの高さ

    def update(self):
        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= PLAYER_SPEED  # 左移動
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += PLAYER_SPEED  # 右移動
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= PLAYER_SPEED  # 上移動
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += PLAYER_SPEED  # 下移動

        # 画面の境界を超えないようにする
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def draw(self):
        # プレイヤーを描画
        pyxel.rect(self.x, self.y, self.width, self.height, 7)  # 白色

class Bullet:
    def __init__(self, x, y):
        self.x = x  # 弾の初期位置X
        self.y = y  # 弾の初期位置Y

    def update(self):
        # 弾の移動
        self.y -= BULLET_SPEED  # 上方向に移動

    def draw(self):
        # 弾を描画
        pyxel.rect(self.x, self.y, 2, 6, 8)  # 青色

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Shooter")  # Pyxelの初期化
        self.player = Player()  # プレイヤーオブジェクト
        self.bullets = []  # 弾のリスト
        pyxel.run(self.update, self.draw)  # メインループの開始

    def update(self):
        # ゲームの更新
        self.player.update()  # プレイヤーの更新
        for bullet in self.bullets:
            bullet.update()  # 弾の更新

        # 弾の発射
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.bullets.append(Bullet(self.player.x + self.player.width // 2, self.player.y))  # 弾を追加

        # 弾のリストから削除
        self.bullets = [b for b in self.bullets if b.y > 0]

    def draw(self):
        # 画面の描画
        pyxel.cls(0)  # 背景を黒に
        self.player.draw()  # プレイヤーを描画
        for bullet in self.bullets:
            bullet.draw()  # 各弾を描画

# ゲームの開始
App()