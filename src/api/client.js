import axios from 'axios';

// In development, CRA can use `proxy` in package.json.
// In production (or when running against a remote backend), set REACT_APP_API_BASE_URL.
const baseURL = process.env.REACT_APP_API_BASE_URL || '';

export const api = axios.create({
  baseURL,
});
