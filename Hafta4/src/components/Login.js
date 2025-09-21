import React, { useState } from 'react';
import { apiService } from '../services/api';
import { useApp } from '../context/AppContext';
import './Login.css';

const Login = () => {
  const [kullaniciAdi, setKullaniciAdi] = useState('');
  const [sifre, setSifre] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setUser, setTicket } = useApp();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await apiService.getTicket(kullaniciAdi, sifre);
      
      if (result.Sonuc && result.ID) {
        setUser({ kullaniciAdi });
        setTicket(result);
      } else {
        setError('Giriş başarısız. Kullanıcı adı veya şifre hatalı.');
      }
    } catch (err) {
      setError('Bağlantı hatası. Lütfen tekrar deneyin.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>DivvyDrive</h1>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <input
              type="text"
              placeholder="Kullanıcı Adı"
              value={kullaniciAdi}
              onChange={(e) => setKullaniciAdi(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Şifre"
              value={sifre}
              onChange={(e) => setSifre(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" disabled={loading}>
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;