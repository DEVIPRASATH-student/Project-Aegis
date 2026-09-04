import { GradientBackground } from "@/components/ui/dark-gradient-background"

export default function Home() {
  return (
    <GradientBackground>
      <div className="flex items-center justify-center min-h-screen w-full">
        <div className="text-center text-white">
          <h1 className="text-4xl font-bold mb-4">Beautiful Gradient Background</h1>
          <p className="text-xl opacity-90">Your content goes here</p>
        </div>
      </div>
    </GradientBackground>
  )
}
