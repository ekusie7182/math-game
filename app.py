import os
import random

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)

# セッションに問題番号や得点を保存するために使用
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key",
)

TOTAL_QUESTIONS = 10


def create_problem():
    """難易度の異なる暗算問題をランダムに生成する。"""
    problem_type = random.randint(1, 5)

    if problem_type == 1:
        # 1桁同士の足し算
        number1 = random.randint(1, 9)
        number2 = random.randint(1, 9)
        operator = "+"
        answer = number1 + number2
        level = "かんたん"
        level_class = "easy"

    elif problem_type == 2:
        # 1桁同士の引き算（答えは負にならない）
        number1 = random.randint(1, 9)
        number2 = random.randint(1, number1)
        operator = "−"
        answer = number1 - number2
        level = "ふつう"
        level_class = "normal"

    elif problem_type == 3:
        # 1桁同士の掛け算
        number1 = random.randint(1, 9)
        number2 = random.randint(1, 9)
        operator = "×"
        answer = number1 * number2
        level = "ふつう"
        level_class = "normal"

    elif problem_type == 4:
        # 2桁同士の足し算
        number1 = random.randint(10, 99)
        number2 = random.randint(10, 99)
        operator = "+"
        answer = number1 + number2
        level = "むずかしい"
        level_class = "hard"

    else:
        # 2桁同士の掛け算
        number1 = random.randint(10, 99)
        number2 = random.randint(10, 99)
        operator = "×"
        answer = number1 * number2
        level = "とてもむずかしい"
        level_class = "very-hard"

    return {
        "number1": number1,
        "number2": number2,
        "operator": operator,
        "answer": answer,
        "level": level,
        "level_class": level_class,
    }


def initialize_game():
    """ゲームを最初の状態に戻す。"""
    session.clear()
    session["question_number"] = 1
    session["score"] = 0
    session["problem"] = create_problem()
    session["last_message"] = ""
    session["message_class"] = ""


@app.route("/")
def title():
    """タイトル画面を表示する。"""
    return render_template("title.html")


@app.route("/start", methods=["POST"])
def start():
    """新しいゲームを開始する。"""
    initialize_game()
    return redirect(url_for("game"))


@app.route("/game", methods=["GET", "POST"])
def game():
    """問題の表示と回答の判定を行う。"""
    if "problem" not in session:
        return redirect(url_for("title"))

    if request.method == "POST":
        problem = session["problem"]
        correct_answer = problem["answer"]

        try:
            user_answer = int(request.form["answer"])

            if user_answer == correct_answer:
                session["score"] += 1
                session["last_message"] = "正解です！"
                session["message_class"] = "correct"
            else:
                session["last_message"] = (
                    f"不正解です。正解は {correct_answer} です。"
                )
                session["message_class"] = "incorrect"

        except (ValueError, TypeError):
            session["last_message"] = "整数を入力してください。"
            session["message_class"] = "incorrect"

        # 10問目の回答後は結果画面へ移動
        if session["question_number"] >= TOTAL_QUESTIONS:
            return redirect(url_for("result"))

        # 次の問題を準備
        session["question_number"] += 1
        session["problem"] = create_problem()

        # ページ再読み込みによる二重回答を防ぐ
        return redirect(url_for("game"))

    return render_template(
        "game.html",
        problem=session["problem"],
        question_number=session["question_number"],
        total_questions=TOTAL_QUESTIONS,
        score=session["score"],
        message=session.get("last_message", ""),
        message_class=session.get("message_class", ""),
    )


@app.route("/result")
def result():
    """10問終了後の結果画面を表示する。"""
    if "score" not in session:
        return redirect(url_for("title"))

    score = session["score"]
    correct_rate = int(score / TOTAL_QUESTIONS * 100)

    return render_template(
        "result.html",
        score=score,
        total_questions=TOTAL_QUESTIONS,
        correct_rate=correct_rate,
    )


@app.route("/back-to-title", methods=["POST"])
def back_to_title():
    """結果画面からタイトル画面へ戻る。"""
    session.clear()
    return redirect(url_for("title"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )