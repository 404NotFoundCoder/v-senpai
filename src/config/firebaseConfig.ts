// Import the functions you need from the SDKs you need
import { initializeApp } from 'firebase/app'
import { getAnalytics } from 'firebase/analytics'
import { getFirestore } from 'firebase/firestore'
import { getDatabase } from 'firebase/database'
import { getAuth, GithubAuthProvider, signInWithPopup, onAuthStateChanged } from 'firebase/auth'
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
// const firebaseConfig = {
//   apiKey: 'AIzaSyDFxXk8tquXOnzyZI4HdLMNJfzbfUKE2so',
//   authDomain: 'v-senpai.firebaseapp.com',
//   projectId: 'v-senpai',
//   storageBucket: 'v-senpai.firebasestorage.app',
//   messagingSenderId: '1019660882427',
//   appId: '1:1019660882427:web:00ce3449de78319bfcbb5e',
//   measurementId: 'G-V9DTTD8FYJ',
// }

const firebaseConfig = {
  apiKey: 'AIzaSyCIUC1RQKxnDyvX0dSdsxmyacSX-DQ30g0',
  authDomain: 'senpi-2cb31.firebaseapp.com',
  projectId: 'senpi-2cb31',
  storageBucket: 'senpi-2cb31.firebasestorage.app',
  messagingSenderId: '370407493684',
  appId: '1:370407493684:web:da012a83ad10ba22563a61',
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const db = getFirestore(app)
const analytics = getAnalytics(app)
const rtdb = getDatabase(app)
const auth = getAuth(app)
const provider = new GithubAuthProvider()

export {
  db,
  app,
  analytics,
  rtdb,
  auth,
  provider,
  signInWithPopup,
  onAuthStateChanged,
  GithubAuthProvider,
}
