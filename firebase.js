// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAFi5auCQfkiFJlXjop6ERM2Z2ulbGqhkI",
  authDomain: "rank-7ec5b.firebaseapp.com",
  projectId: "rank-7ec5b",
  storageBucket: "rank-7ec5b.appspot.com",
  messagingSenderId: "102120392342",
  appId: "1:102120392342:web:ed4a55336e1f7228c864b7",
  measurementId: "G-BDPTVFX8VX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);