import axios from 'axios';

const BASE_URL = '/api/';
const BASIC_AUTH = btoa('NDSServis:ca5094ef-eae0-4bd5-a94a-14db3b8f3950');

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300000,
  headers: {
    'Authorization': `Basic ${BASIC_AUTH}`,
    'Content-Type': 'application/json'
  }
});

api.interceptors.response.use(
  response => {
    console.log('API Response:', response.config.url, response.data);
    return response;
  },
  error => {
    console.error('API Error:', error.config?.url, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  async getTicket(kullaniciAdi, sifre) {
    const response = await api.post('TicketAl', {
      kullaniciAdi,
      sifre
    });
    return response.data;
  },

  async getFolders(ticketID, klasorYolu = '') {
    const params = new URLSearchParams({
      ticketID: ticketID.toString(),
      klasorYolu: klasorYolu
    });
    const response = await api.get(`KlasorListesiGetir?${params}`);
    return response.data;
  },

  async createFolder(ticketID, klasorAdi, klasorYolu = '') {
    const response = await api.post('KlasorOlustur', {
      ticketID,
      klasorAdi,
      klasorYolu
    });
    return response.data;
  },

  async deleteFolder(ticketID, klasorAdi, klasorYolu) {
    const response = await api.delete('KlasorSil', {
      data: {
        ticketID,
        klasorAdi,
        klasorYolu
      }
    });
    return response.data;
  },

  async updateFolder(ticketID, klasorAdi, klasorYolu, yeniKlasorAdi) {
    const response = await api.put('KlasorGuncelle', {
      ticketID,
      klasorAdi,
      klasorYolu,
      yeniKlasorAdi
    });
    return response.data;
  },

  async moveFolder(ticketID, klasorAdi, klasorYolu, yeniKlasorYolu) {
  try {
    const response = await api.put('KlasorTasi', {
      ticketID,
      klasorAdi,
      klasorYolu,
      yeniKlasorYolu
    });
    console.log('Move folder result:', response.data);
    return response.data;
  } catch (error) {
    console.error('Move folder error:', error);
    throw error;
  }
},

  async getFiles(ticketID, klasorYolu = '') {
  try {
    const response = await api.get('DosyaListesiGetir', {
      params: {
        ticketID: ticketID,
        klasorYolu: klasorYolu
      }
    });
    
    console.log('Raw files API response:', response.data);
    console.log('Files list from API:', response.data.SonucDosyaListe);
    
    return response.data;
  } catch (error) {
    console.error('getFiles error:', error);
    throw error;
  }
},

  async createFile(ticketID, dosyaAdi, klasorYolu = '') {
    const response = await api.post('DosyaOlustur', {
      ticketID,
      dosyaAdi,
      klasorYolu
    });
    return response.data;
  },

  async deleteFile(ticketID, dosyaAdi, klasorYolu) {
    const response = await api.delete('DosyaSil', {
      data: {
        ticketID,
        dosyaAdi,
        klasorYolu
      }
    });
    return response.data;
  },

  async updateFile(ticketID, dosyaAdi, klasorYolu, yeniDosyaAdi) {
    const response = await api.put('DosyaGuncelle', {
      ticketID,
      dosyaAdi,
      klasorYolu,
      yeniDosyaAdi
    });
    return response.data;
  },

  async moveFile(ticketID, dosyaAdi, klasorYolu, yeniDosyaYolu) {
  try {
    const response = await api.put('DosyaTasi', {
      ticketID,
      dosyaAdi,
      klasorYolu,
      yeniDosyaYolu
    });
    console.log('Move file result:', response.data);
    return response.data;
  } catch (error) {
    console.error('Move file error:', error);
    throw error;
  }
},

  async createFileMetaData(ticketID, dosyaAdi, parcaSayisi, herBirParcaninBoyutuByte) {
    const response = await api.post('DosyaMetaDataKaydiOlustur', {
      ticketID,
      dosyaAdi,
      parcaSayisi,
      herBirParcaninBoyutuByte
    });
    return response.data;
  },

  async uploadFilePart(ticketID, tempKlasorID, parcaHash, parcaNumarasi, chunkData) {
  try {
    console.log('=== CHUNK UPLOAD START ===');
    
    const params = new URLSearchParams({
      ticketID: ticketID.toString(),
      tempKlasorID: tempKlasorID.toString(),
      parcaHash: parcaHash,
      parcaNumarasi: parcaNumarasi.toString()
    });
    
    const response = await api.post(`DosyaParcalariYukle?${params}`, chunkData, {
      headers: {
        'Content-Type': 'application/octet-stream'
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
      timeout: 120000,
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Chunk ${parcaNumarasi} progress:`, percentCompleted + '%');
      }
    });
    
    return response.data;
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      throw new Error(`Chunk ${parcaNumarasi} yükleme zaman aşımına uğradı.`);
    }
    throw error;
  }
},

  async publishFile(ticketID, ID, dosyaAdi, klasorYolu) {
    const response = await api.post('DosyaYayinla', {
      ticketID,
      ID,
      dosyaAdi,
      klasorYolu
    });
    return response.data;
  },

  async uploadFileDirect(ticketID, dosyaAdi, klasorYolu, dosyaHash, fileData) {
  try {
    console.log('=== DIRECT UPLOAD START ===');
    
    const params = new URLSearchParams({
      ticketID: ticketID.toString(),
      dosyaAdi: dosyaAdi,
      klasorYolu: klasorYolu,
      dosyaHash: dosyaHash
    });
    
    const response = await api.post(`DosyaDirektYukle?${params}`, fileData, {
      headers: {
        'Content-Type': 'application/octet-stream'
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
      timeout: 300000, 
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log('Upload progress:', percentCompleted + '%');
      }
    });
    
    return response.data;
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      throw new Error('Yükleme zaman aşımına uğradı. Dosya çok büyük olabilir.');
    }
    throw error;
  }
  },

  async downloadFile(ticketID, indirilecekYol, klasorYolu, dosyaAdi) {
  try {
    const response = await api.post('DosyaIndir', {
      ticketID,
      indirilecekYol,
      klasorYolu,
      dosyaAdi
    }, {
      responseType: 'blob'
    });
    
    console.log('Download response received');
    return response.data;
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
}
};