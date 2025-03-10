import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import CameraDevicesProvider from "@/providers/CameraDevicesProvider";
import type { Metadata, Viewport } from "next";
import { Roboto } from "next/font/google";
// import localFont from "next/font/local";
import "./globals.css";
import BottomNavbar from "@/components/navbar/bottom-navbar";
// import PlantNotification from "@/components/plant-notification";
// import Dark from "@/components/DarkMode";
const roboto = Roboto({
  subsets: ["latin"],
  weight: ["400", "900"],
});
export const viewport: Viewport = {
  themeColor: "#8FCE00",
};

export const metadata: Metadata = {
  title: "nurtiVision",
  description:
    "nurtiVision is nutrition tracking app that helps you to track your daily nutrition intake and helps you to maintain a healthy lifestyle.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* <link
          rel="icon"
          type="image/png"
          // href="/favicon-48x48.png"
          sizes="48x48"
        /> */}
        {/* <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="shortcut icon" href="/favicon.ico" /> */}
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/apple-touch-icon.png"
        />
        <meta name="apple-mobile-web-app-title" content="nurtiVision" />
        <link rel="manifest" href="/site.webmanifest" />
        <script async src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs/"></script>
      </head>
      <body className={`${roboto.className} antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="white">  
          

          <CameraDevicesProvider>{children}</CameraDevicesProvider>
          <Toaster />
          <BottomNavbar />
       
        </ThemeProvider>

      </body>
    </html>
  );
}
