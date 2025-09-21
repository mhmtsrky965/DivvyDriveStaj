import CryptoJS from 'crypto-js';

export const FileUtils = {
  splitFile(file, chunkSize = 1024 * 1024) {
    const chunks = [];
    let start = 0;
    
    while (start < file.size) {
      const end = Math.min(start + chunkSize, file.size);
      chunks.push(file.slice(start, end));
      start = end;
    }
    
    console.log(`File ${file.name} split into ${chunks.length} chunks`);
    return chunks;
  },

  async calculateMD5Hash(data) {
    try {
      console.log('Calculating MD5 hash for:', data.name || 'chunk', 'size:', data.size);
      
      const arrayBuffer = await data.arrayBuffer();
      
      const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
      
      const hash = CryptoJS.MD5(wordArray).toString();
      
      console.log('MD5 hash calculated:', hash);
      return hash;
    } catch (error) {
      console.error('MD5 hash calculation failed:', error);
      throw new Error('MD5 hash hesaplama başarısız: ' + error.message);
    }
  },

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    if (bytes < 0) return 'Unknown';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
};