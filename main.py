import streamlit as st


# 약수를 구하는 함수
def get_divisors(n: int):
return [i for i in range(1, n + 1) if n % i == 0]


st.title("약수 찾기 프로그램")


number = st.number_input("숫자를 입력하세요", min_value=1, step=1)


if st.button("약수 찾기"):
divisors = get_divisors(int(number))
st.write(f"**{int(number)}의 약수:**")
st.write(divisors)
