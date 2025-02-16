import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const cameraUrl = 'http://10.19.183.152:5001/video_feed';
  try {
    const response = await fetch(cameraUrl);
    const arrayBuffer = await response.arrayBuffer();
    const contentType = response.headers.get('content-type') || 'image/jpeg';
    res.setHeader('Content-Type', contentType);
    // Optionally allow CORS if used in a client hosted domain
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 'no-store');
    res.send(Buffer.from(arrayBuffer));
  } catch (error) {
    res.status(500).end('Error fetching camera stream');
  }
}