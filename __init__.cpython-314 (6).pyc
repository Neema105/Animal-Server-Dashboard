from dataclasses import dataclass

from repositories.user_repository import FileUserRepository
from utils.security import hash_password, is_hashed_password, verify_password

#authentication
@dataclass
class AuthResult:
    auth_ok: bool
    login_message: str = ""
    create_message: str = ""
    question_message: str = ""
    forgot_message: str = ""


class AuthService:
    def __init__(self, user_repository: FileUserRepository):
        self.user_repository = user_repository

    def create_user(self, username: str, password: str, question: str, answer: str) -> AuthResult:
        users = self.user_repository.load_users()
        username = (username or "").strip()

        if not all([username, password, question, answer]):
            return AuthResult(False, create_message="Fill in all create-user fields.")
        if username in users:
            return AuthResult(False, create_message="Username already exists.")

        users[username] = {"password": hash_password(password), "question": question, "answer": answer}
        self.user_repository.save_users(users)
        return AuthResult(False, create_message=f"User {username} created.")

    def reset_password(self, username: str, answer: str, new_password: str) -> AuthResult:
        users = self.user_repository.load_users()
        username = (username or "").strip()
        user = users.get(username)

        if not user:
            return AuthResult(False, question_message="User not found.")
        if not answer or not new_password:
            return AuthResult(
                False,
                question_message=f"Question: {user['question']}",
                forgot_message="Enter the answer and a new password.",
            )
        if answer != user["answer"]:
            return AuthResult(
                False,
                question_message=f"Question: {user['question']}",
                forgot_message="Security answer is incorrect.",
            )

        users[username]["password"] = hash_password(new_password)
        self.user_repository.save_users(users)
        return AuthResult(
            False,
            question_message=f"Question: {user['question']}",
            forgot_message="Password updated.",
        )

    def login(self, username: str, password: str) -> AuthResult:
        users = self.user_repository.load_users()
        username = (username or "").strip()
        user = users.get(username, {})
        stored_password = user.get("password", "")
        auth_ok = verify_password(password, stored_password)

        if auth_ok and stored_password and not is_hashed_password(stored_password):
            users[username]["password"] = hash_password(password)
            self.user_repository.save_users(users)

        self.user_repository.append_login_attempt(username, auth_ok)
        return AuthResult(auth_ok, login_message="" if auth_ok else "Login failed.")
