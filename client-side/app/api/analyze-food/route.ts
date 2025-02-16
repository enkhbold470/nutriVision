// app/api/hello/route.ts
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // You can access query parameters or headers from the request if needed
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name') || 'World';

  // Return a JSON response
  return NextResponse.json({ message: `Hello, ${name}!` });
}