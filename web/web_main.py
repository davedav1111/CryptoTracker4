# import streamlit as st
# import requests

# # 注册功能
# import streamlit as st
# import requests

# def register():
#     st.title("Register")
#     username = st.text_input("Username")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if st.button("Register"):
#         try:
#             # 发送注册请求到后端
#             response = requests.post(
#                 "http://127.0.0.1:8000/users/",  # 确保地址正确
#                 json={"username": username, "email": email, "password": password, "role": "user"},
#                 timeout=10,  # 设置超时时间，防止长时间等待
#             )

#             # 处理响应
#             if response.status_code == 200:
#                 st.success("Registration successful! You can now log in.")
#             elif response.status_code == 400:
#                 st.error("Registration failed: Email already registered.")
#             else:
#                 # 输出后端返回的错误详情
#                 st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")

#         except requests.exceptions.ConnectionError:
#             st.error("Could not connect to the backend. Please ensure the backend server is running.")
#         except requests.exceptions.Timeout:
#             st.error("The request timed out. Please try again.")
#         except Exception as e:
#             st.error(f"An unexpected error occurred: {str(e)}")


# # 登录功能
# def login():
#     st.title("Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         response = requests.post(
#             "http://localhost:8000/token",
#             data={"username": email, "password": password},
#         )
#         if response.status_code == 200:
#             st.success("Login successful!")
#             st.session_state["token"] = response.json()["access_token"]
#         else:
#             st.error("Login failed. Please check your email and password.")

# import streamlit as st
# import requests

# # 初始化 Session State
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# # Login 功能
# def login():
#     st.title("Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         response = requests.post(
#             "http://localhost:8000/token",
#             data={"username": email, "password": password},
#         )
#         if response.status_code == 200:
#             st.success("Login successful!")
#             st.session_state.logged_in = True  # 更新登录状态
#             st.experimental_set_query_params(page="dashboard")  # 切换到 Dashboard
#         else:
#             st.error("Login failed. Please check your email and password.")

# # Dashboard 功能
# def dashboard():
#     st.title("Dashboard")
#     st.write("Welcome to your dashboard!")

#     if st.button("Logout"):
#         st.session_state.logged_in = False  # 更新登录状态
#         st.experimental_set_query_params(page="login")  # 回到登录页面

# # 页面导航逻辑
# def main():
#     # 获取当前页面参数
#     query_params = st.experimental_get_query_params()
#     page = query_params.get("page", ["login"])[0]

#     # 动态导航
#     if st.session_state.logged_in:
#         dashboard()  # 如果已经登录，显示 Dashboard
#     elif page == "dashboard":
#         st.warning("You must log in to access the dashboard.")
#         login()  # 未登录时显示登录页面
#     else:
#         login()  # 默认显示登录页面

# if __name__ == "__main__":
#     main()


# # # 仪表盘功能
# # def dashboard():
# #     st.title("Dashboard")
# #     if "token" not in st.session_state:
# #         st.error("Please login first!")
# #         return

# #     headers = {"Authorization": f"Bearer {st.session_state['token']}"}
# #     response = requests.get("http://localhost:8000/portfolio/1", headers=headers)

# #     if response.status_code == 200:
# #         portfolio = response.json()
# #         st.subheader("Portfolio Overview")
# #         total_value = sum(item["quantity"] * item["current_price"] for item in portfolio)
# #         st.metric("Total Value", f"${total_value:.2f}")

# #         st.subheader("Holdings")
# #         for item in portfolio:
# #             st.write(f"{item['coin_id']}: {item['quantity']} @ ${item['current_price']:.2f}")
# #     else:
# #         st.error("Failed to load portfolio data.")

# # # 加密货币搜索功能
# # def crypto_search():
# #     st.title("Crypto Search")
# #     coin_id = st.text_input("Enter coin ID (e.g., bitcoin)")

# #     if st.button("Search"):
# #         response = requests.get(f"http://localhost:8000/crypto/{coin_id}")
# #         if response.status_code == 200:
# #             data = response.json()
# #             st.write(f"Name: {coin_id}")
# #             st.write(f"Current Price: ${data['current_price']}")
# #             st.write(f"Market Cap: ${data['market_cap']}")
# #         else:
# #             st.error("Coin not found.")

# # # 主导航
# # def main():
# #     st.sidebar.title("Navigation")
# #     menu = st.sidebar.radio("Go to", ["Register", "Login", "Dashboard", "Crypto Search"])

# #     if menu == "Register":
# #         register()
# #     elif menu == "Login":
# #         login()
# #     elif menu == "Dashboard":
# #         dashboard()
# #     elif menu == "Crypto Search":
# #         crypto_search()

# # if __name__ == "__main__":
# #     main()

import streamlit as st
import requests

# 初始化 Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "token" not in st.session_state:
    st.session_state.token = None


# 注册功能
def register():
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            # 发送注册请求到后端
            response = requests.post(
                "http://127.0.0.1:8000/users/",
                json={"username": username, "email": email, "password": password, "role": "user"},
                timeout=10,
            )

            if response.status_code == 200:
                st.success("Registration successful! You can now log in.")
                st.experimental_set_query_params(page="login")  # 跳转到登录页面
            elif response.status_code == 400:
                st.error("Registration failed: Email already registered.")
            else:
                st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend. Please ensure the backend server is running.")
        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")


# 登录功能
def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = requests.post(
                "http://localhost:8000/token",
                data={"username": email, "password": password},
            )
            if response.status_code == 200:
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.token = response.json()["access_token"]
                st.experimental_set_query_params(page="dashboard")  # 跳转到 Dashboard
            else:
                st.error("Login failed. Please check your email and password.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


# Dashboard 功能
def dashboard():
    st.title("Dashboard")
    st.write("Welcome to your dashboard!")
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get("http://localhost:8000/portfolio/1", headers=headers)  # 替换用户ID
        if response.status_code == 200:
            portfolio_data = response.json()
            st.write("Portfolio Data:", portfolio_data)
        else:
            st.warning("Failed to fetch portfolio data.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_set_query_params(page="welcome")  # 返回欢迎页面


# 欢迎页面
def welcome():
    st.title("Welcome!")
    st.write("Please choose an option below:")
    if st.button("Register"):
        st.experimental_set_query_params(page="register")
    if st.button("Login"):
        st.experimental_set_query_params(page="login")


# 页面导航逻辑
def main():
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["welcome"])[0]

    if st.session_state.logged_in:
        dashboard()
    elif page == "register":
        register()
    elif page == "login":
        login()
    else:
        welcome()


if __name__ == "__main__":
    main()

