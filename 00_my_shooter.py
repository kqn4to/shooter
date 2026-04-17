# title: Pyxel Shooter
# author: Takashi Kitao
# desc: A Pyxel shoot'em up game example
# site: https://github.com/kitao/pyxel
# license: MIT
# version: 1.0

import pyxel

# シーン状態（タイトル/プレイ中/ゲームオーバー）を表す定数
SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2

# 背景の星の描画設定
NUM_STARS = 100
STAR_COLOR_HIGH = 12
STAR_COLOR_LOW = 5

# プレイヤーの当たり判定サイズと移動速度
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 8
PLAYER_SPEED = 2

# 弾の見た目と移動設定
BULLET_WIDTH = 2
BULLET_HEIGHT = 8
BULLET_COLOR = 11
BULLET_SPEED = 4

# 敵キャラクターの当たり判定サイズと移動速度
ENEMY_WIDTH = 8
ENEMY_HEIGHT = 8
ENEMY_SPEED = 1.5

# 撃破時のブラスト（円形エフェクト）の設定
BLAST_START_RADIUS = 1
BLAST_END_RADIUS = 8
BLAST_COLOR_IN = 7
BLAST_COLOR_OUT = 10

# エンティティ（動的オブジェクト）を種類ごとに管理するリスト
enemies = []
bullets = []
blasts = []
items = []
explosions = []
# 全エンティティ群をタプル化し、更新/描画/掃除を一括で処理する
ENTITY_GROUPS = (enemies, bullets, blasts, items, explosions)


def update_entities(entities):
    # 各エンティティの1フレーム分の更新を実行
    for entity in entities:
        entity.update()


def draw_entities(entities):
    # 各エンティティの描画処理を実行
    for entity in entities:
        entity.draw()


def cleanup_entities(entities):
    # is_alive=False の要素を取り除いてメモリと描画対象を整理
    entities[:] = [e for e in entities if e.is_alive]


def update_all_entities():
    # 全エンティティ群をまとめて更新（エンティティ管理システムの中核）
    for entities in ENTITY_GROUPS:
        update_entities(entities)


def cleanup_all_entities():
    # 全エンティティ群をまとめて掃除（死亡エンティティの除去）
    for entities in ENTITY_GROUPS:
        cleanup_entities(entities)


def clear_all_entities():
    # シーン切り替え時などに全エンティティを完全初期化
    for entities in ENTITY_GROUPS:
        entities.clear()


def is_colliding_rect(a, b):
    # AABB（軸平行矩形）による衝突判定
    # 2つの矩形が x/y 両軸で重なっているとき True
    return (
        a.x + a.w > b.x
        and b.x + b.w > a.x
        and a.y + a.h > b.y
        and b.y + b.h > a.y
    )


class Background:
    # 背景スクロール（星空）を管理するクラス
    def __init__(self):
        self.stars = [
            (
                pyxel.rndi(0, pyxel.width - 1),
                pyxel.rndi(0, pyxel.height - 1),
                pyxel.rndf(1, 2.5),
            )
            for _ in range(NUM_STARS)
        ]

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            y += speed
            if y >= pyxel.height:
                y -= pyxel.height
            self.stars[i] = (x, y, speed)

    def draw(self):
        for x, y, speed in self.stars:
            pyxel.pset(x, y, STAR_COLOR_HIGH if speed > 1.8 else STAR_COLOR_LOW)


class Player:
    # プレイヤー本体（移動、射撃、ボム使用）を管理するクラス
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.item = None
        self.parent = parent
        self.is_alive = True

    def update(self):
        # キー入力に応じて移動
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.x -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.x += PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.y -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.y += PLAYER_SPEED

        self.x = pyxel.clamp(self.x, 0, GAME_WIDTH - self.w)
        self.y = pyxel.clamp(self.y, 0, pyxel.height - self.h)

        # 発射入力で弾を生成
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            Bullet(
                self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2
            )
            pyxel.play(3, 0)

        # ボム所持中に R キーで全敵を一掃
        if pyxel.btnp(pyxel.KEY_R) and self.item:
            # Bomb effect: clear all enemies
            for enemy in enemies:
                Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2)
            enemies.clear()
            self.item = None

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 0, self.w, self.h, 0)


class Bullet:
    # プレイヤーの弾を表すクラス
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        bullets.append(self)

    def update(self):
        self.y -= BULLET_SPEED
        if self.y + self.h - 1 < 0:
            self.is_alive = False

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, BULLET_COLOR)


class Enemy:
    # 左右に揺れながら下降する敵を表すクラス
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.dir = 1
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        enemies.append(self)

    def update(self):
        if (pyxel.frame_count + self.timer_offset) % 60 < 30:
            self.x += ENEMY_SPEED
            self.dir = 1
        else:
            self.x -= ENEMY_SPEED
            self.dir = -1

        self.y += ENEMY_SPEED

        if self.y > pyxel.height - 1:
            self.is_alive = False

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 8, 0, self.w * self.dir, self.h, 0)


class Blast:
    # 敵撃破時に表示する円形ブラストエフェクト
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True
        blasts.append(self)

    def update(self):
        self.radius += 1
        if self.radius > BLAST_END_RADIUS:
            self.is_alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
        pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)


class Item:
    # 取得するとボムを使えるアイテム
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.is_alive = True
        items.append(self)

    def update(self):
        self.y += 1.5
        if self.y > pyxel.height:
            self.is_alive = False

    def draw(self):
        # Bomb icon
        pyxel.circ(self.x + 4, self.y + 4, 3, 8)
        pyxel.circ(self.x + 4, self.y + 3, 1, 7)
        pyxel.pset(self.x + 4, self.y + 1, 7)


class Explosion:
    # 画面演出用の爆発エフェクト
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 15
        self.is_alive = True
        explosions.append(self)

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.is_alive = False

    def draw(self):
        # Expanding circle effect
        radius = 15 - self.timer
        if radius > 0:
            pyxel.circ(self.x, self.y, radius, 10)
            pyxel.circ(self.x, self.y, radius - 2, 7)


GAME_WIDTH = 120
UI_WIDTH = 40
# ハイスコア保存先ファイル
HIGH_SCORE_FILE = "highscore.txt"


class App:
    # ゲーム全体（初期化、シーン管理、更新、描画）を統括するクラス
    def __init__(self):
        pyxel.init(GAME_WIDTH + UI_WIDTH, 160, title="Pyxel Shooter")

        self.init_image()
        self.init_sound()

        self.scene = SCENE_TITLE
        self.score = 0
        self.play_time = 0
        self.high_score = self.load_high_score()
        self.background = Background()
        self.player = Player(GAME_WIDTH / 2, pyxel.height - 20, self)
        self.explosions = []

        pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def load_high_score(self):
        # 起動時にハイスコアを読み込む（失敗時は 0）
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        # ハイスコア更新時にファイルへ保存
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def init_image(self):
        # Set player image
        pyxel.images[0].set(
            0,
            0,
            [
                "00c00c00",
                "0c7007c0",
                "0c7007c0",
                "c703b07c",
                "77033077",
                "785cc587",
                "85c77c58",
                "0c0880c0",
            ],
        )

        # Set enemy image
        pyxel.images[0].set(
            8,
            0,
            [
                "00088000",
                "00ee1200",
                "08e2b180",
                "02882820",
                "00222200",
                "00012280",
                "08208008",
                "80008000",
            ],
        )

    def init_sound(self):
        # Set sound effects
        pyxel.sounds[0].set("a3a2c1a1", "p", "7", "s", 5)
        pyxel.sounds[1].set("a3a2c2c2", "n", "7742", "s", 10)

        # Set title music
        a1 = "T128 Q96 @2 @ENV1{127,6,96} O4 L16 @VIB1{36,18,25} K-2"
        a2 = "D8.C8.D4G8AB->CD C8.<F2R FFGA B-8.A8.B-4.GGAB-"
        a3 = "RR>CC<B->C8 D8.D8CD8.<"

        b1 = "T128 Q90 @0 V96 O3 L16"
        b2 = "FFR4 FFR4 <F4> E-E-R4 E-E-R4 <E-4> D-D-R4 D-D-R4 <D-4> E-E-R4 E-E-R4 EEE8"

        c1 = "T128 Q50 @3 L16 @ENV1{48,8,0} @ENV2{127,6,0}"
        c2 = "[@ENV1 O7 FFR4 FFR4 @ENV2 O3 G4]3 @ENV1 O7 FFR4 FFR4 FF @ENV2 O3 G8"

        pyxel.sounds[2].mml(a1 + a2 + a3)
        pyxel.sounds[3].mml(b1 + b2)
        pyxel.sounds[4].mml(c1 + c2)
        pyxel.musics[0].set([2], [3], [4])

        # Set play music
        a1 = "T150 Q96 @1 @ENV1{127,12,64} O4 L16"
        a4 = "RR>CC<B->C8 D8.D8C<A8G&1"

        b1 = "T150 Q96 @1 @ENV1{112,12,56} @ENV2{64,8,0} O4 L16 @ENV1 "
        b2 = "<B-8.A8.B-4>D8DDGB- A8.<A2R AA>CF G8.F8.G4.E-E-FG"
        b3 = "RRAAGA8 A8.A8GA8."
        b4 = "RRAAGA8 A8.A8GD8 Q100 C&4.<B4. @3 O7 @ENV2 FFFF"

        c1 = "T150 Q100 @0 V96 O3 L16 @GLI1{400,4} @GLI0 "
        c2 = "[<G.R32>DG]4 [<F.R32>CF]4 [<E-.R32B->E-]4"
        c3 = "Q80 <F8FF>F<F8 F+8RF+8>F+<F+8.>"
        c4 = "Q80 @GLI0 <F8FF>F<F8F+8RF+8>F+<F+8 Q100 G8R>DG<[G.R32>DG<]2 @GLI1 Q50 >>CC<F8>"

        pyxel.sounds[5].mml(a1 + a2 + a3 + a2 + a4)
        pyxel.sounds[6].mml(b1 + b2 + b3 + b2 + b4)
        pyxel.sounds[7].mml(c1 + c2 + c3 + c2 + c4)
        pyxel.musics[1].set([5], [6], [7])

    def update(self):
        # 現在のシーンに応じて更新処理を分岐
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        self.background.update()

        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            self.update_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover_scene()

    def update_title_scene(self):
        # タイトル画面: Enter/Start でプレイ開始
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
            self.scene = SCENE_PLAY
            pyxel.playm(1, loop=True)

    def enter_gameover_scene(self):
        # ゲームオーバー遷移: BGM停止、SE再生、ハイスコア更新
        pyxel.stop()
        pyxel.play(3, 1)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.scene = SCENE_GAMEOVER

    def reset_play_state(self):
        # リトライ時のプレイ状態初期化
        self.scene = SCENE_PLAY
        self.player.x = GAME_WIDTH / 2
        self.player.y = pyxel.height - 20
        self.score = 0
        self.play_time = 0
        self.player.item = None
        clear_all_entities()
        pyxel.playm(1, loop=True)

    def update_play_scene(self):
        # 一定間隔で敵とアイテムをスポーン
        if pyxel.frame_count % 6 == 0:
            Enemy(pyxel.rndi(0, GAME_WIDTH - ENEMY_WIDTH), 0)

        if pyxel.frame_count % 120 == 0:
            Item(pyxel.rndi(0, GAME_WIDTH - 8), 0)

        # 衝突判定1: 敵と弾が重なったら双方を消し、スコア加算
        for enemy in enemies:
            for bullet in bullets:
                if is_colliding_rect(enemy, bullet):
                    enemy.is_alive = False
                    bullet.is_alive = False
                    Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2)
                    pyxel.play(2, 1, resume=True)
                    self.score += 10

        # 衝突判定2: プレイヤーとアイテムが重なったらボム取得
        for item in items:
            if is_colliding_rect(self.player, item):
                self.player.item = "bomb"
                item.is_alive = False

        # 衝突判定3: プレイヤーと敵が重なったらゲームオーバー
        for enemy in enemies:
            if is_colliding_rect(self.player, enemy):
                enemy.is_alive = False
                Blast(
                    self.player.x + PLAYER_WIDTH / 2,
                    self.player.y + PLAYER_HEIGHT / 2,
                )
                self.enter_gameover_scene()

        # 生存ボーナス（1秒ごと）でスコア加算
        self.play_time += 1
        if self.play_time % 60 == 0:
            self.score += 5

        self.player.update()

        # 全エンティティを更新して不要要素を削除
        update_all_entities()
        cleanup_all_entities()

    def update_gameover_scene(self):
        # ゲームオーバー中も演出エンティティのみ更新
        update_all_entities()
        cleanup_all_entities()

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
            self.reset_play_state()

    def draw(self):
        # 共通背景を描画後、シーン別描画へ分岐
        pyxel.cls(0)
        self.background.draw()

        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()

        # Draw separator line
        pyxel.line(GAME_WIDTH, 0, GAME_WIDTH, pyxel.height, 7)

        # Draw right panel background
        pyxel.rect(GAME_WIDTH + 1, 0, UI_WIDTH - 1, pyxel.height, 0)

        # UI: Score top-right
        pyxel.text(GAME_WIDTH + 5, 10, "SCORE", 7)
        pyxel.text(GAME_WIDTH + 5, 20, f"{self.score}", 7)
        pyxel.text(GAME_WIDTH + 5, 35, "HIGH", 7)
        pyxel.text(GAME_WIDTH + 5, 45, f"{self.high_score}", 7)

        # UI: Item box bottom-right (black bg, white border)
        pyxel.rect(GAME_WIDTH + 5, 130, 30, 25, 0)
        pyxel.rectb(GAME_WIDTH + 5, 130, 30, 25, 7)
        if self.player.item:
            # Bomb icon (centered in 30x25 box)
            pyxel.circ(GAME_WIDTH + 20, 140, 6, 8)
            pyxel.circ(GAME_WIDTH + 20, 138, 2, 7)
            pyxel.pset(GAME_WIDTH + 20, 136, 7)




    def draw_title_scene(self):
        pyxel.clip(0, 0, GAME_WIDTH, 160)
        pyxel.text(30, 66, "Pyxel Shooter", pyxel.frame_count % 16)
        pyxel.text(26, 126, "- PRESS ENTER -", 13)
        pyxel.clip()

    def draw_play_scene(self):
        pyxel.clip(0, 0, GAME_WIDTH, 160)
        self.player.draw()

        draw_entities(bullets)
        draw_entities(enemies)
        draw_entities(blasts)
        draw_entities(items)
        draw_entities(explosions)
        pyxel.clip()

    def draw_gameover_scene(self):
        pyxel.clip(0, 0, GAME_WIDTH, 160)
        draw_entities(bullets)
        draw_entities(enemies)
        draw_entities(blasts)
        draw_entities(items)
        draw_entities(explosions)
        pyxel.clip()

        pyxel.text(38, 66, "GAME OVER", 8)
        pyxel.text(26, 126, "- PRESS ENTER -", 13)


App()
