import streamlit as st
import pandas as pd
from datetime import datetime
import os
from github import Github

# Inisialisasi data rental
def load_data():
    try:
        data = pd.read_csv("rental_data.csv")
    except FileNotFoundError:
        data = pd.DataFrame(columns=["User", "E-Bike ID", "Start Time", "End Time", "Status"])
        data.to_csv("rental_data.csv", index=False)
    return data

def save_data(data):
    data.to_csv("rental_data.csv", index=False)

# Fungsi untuk menyewa E-Bike
def rent_bike(user, bike_id):
    data = load_data()
    if (data["E-Bike ID"] == bike_id).any() and (data["Status"] == "Rented").any():
        return f"E-Bike {bike_id} is currently rented."
    else:
        new_entry = {
            "User": user,
            "E-Bike ID": bike_id,
            "Start Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "End Time": "",
            "Status": "Rented"
        }
        data = data.append(new_entry, ignore_index=True)
        save_data(data)
        return f"E-Bike {bike_id} successfully rented by {user}."

# Fungsi untuk mengembalikan E-Bike
def return_bike(user, bike_id):
    data = load_data()
    if ((data["User"] == user) & (data["E-Bike ID"] == bike_id) & (data["Status"] == "Rented")).any():
        data.loc[(data["User"] == user) & (data["E-Bike ID"] == bike_id), "End Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.loc[(data["User"] == user) & (data["E-Bike ID"] == bike_id), "Status"] = "Returned"
        save_data(data)
        return f"E-Bike {bike_id} successfully returned by {user}."
    else:
        return f"No matching rental record found for E-Bike {bike_id} and user {user}."

# Fungsi untuk melihat log rental
def view_logs():
    data = load_data()
    return data

# Fungsi untuk menghubungkan ke GitHub dan menyinkronkan data
def sync_to_github(file_path, repo_name, token, commit_message):
    try:
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)
        with open(file_path, "r") as file:
            content = file.read()
        file_name = os.path.basename(file_path)
        try:
            file_content = repo.get_contents(file_name)
            repo.update_file(file_content.path, commit_message, content, file_content.sha)
        except:
            repo.create_file(file_name, commit_message, content)
        st.success("Data successfully uploaded to GitHub.")
    except Exception as e:
        st.error(f"Error uploading to GitHub: {e}")

# Streamlit UI
st.title("E-Bike Rental Management System")

# Tab navigasi
menu = st.sidebar.selectbox("Menu", ["Rent E-Bike", "Return E-Bike", "View Logs", "Sync to GitHub"])

data = load_data()

if menu == "Rent E-Bike":
    st.header("Rent an E-Bike")
    user = st.text_input("Enter your name")
    bike_id = st.text_input("Enter E-Bike ID")
    if st.button("Rent"):
        if user and bike_id:
            st.success(rent_bike(user, bike_id))
        else:
            st.error("Please provide both name and E-Bike ID.")

elif menu == "Return E-Bike":
    st.header("Return an E-Bike")
    user = st.text_input("Enter your name")
    bike_id = st.text_input("Enter E-Bike ID")
    if st.button("Return"):
        if user and bike_id:
            st.success(return_bike(user, bike_id))
        else:
            st.error("Please provide both name and E-Bike ID.")

elif menu == "View Logs":
    st.header("Rental Logs")
    st.dataframe(data)

elif menu == "Sync to GitHub":
    st.header("Sync Logs to GitHub")
    repo_name = st.text_input("Enter GitHub repository name (e.g., username/repo)")
    token = st.text_input("Enter GitHub Personal Access Token", type="password")
    if st.button("Sync"):
        if repo_name and token:
            sync_to_github("rental_data.csv", repo_name, token, "Update rental logs")
        else:
            st.error("Please provide both repository name and token.")
