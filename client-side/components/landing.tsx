"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import {Input} from "@/components/ui/input"
export default function Home() {
  const [age, setAge] = useState("")
  const [gender, setGender] = useState("")
  const [height, setHeight] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Here you would typically save this data to a state management solution or API
    router.push("/goal")
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4 ">Fitness Tracker</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="age" className="block text-sm font-medium ">
            Age
          </label>
          <Input
            type="number"
            id="age"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            className="mt-1 block w-full rounded-md border shadow-sm "
            required
          />
        </div>
        <div>
          <label htmlFor="gender" className="block text-sm font-medium ">
            Gender
          </label>
          <select
            id="gender"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className="mt-1 block w-full rounded-md border shadow-sm "
            required
          >
            <option value="">Select gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label htmlFor="height" className="block text-sm font-medium ">
            Height (cm)
          </label>
          <Input
            type="number"
            id="height"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            className="mt-1 block w-full rounded-md border shadow-sm "
            required
          />
        </div>
        <Button
          type="submit"
          className="w-full py-2 px-4 rounded-md  focus:outline-none focus:ring-2  focus:ring-offset-2"
        >
          Next
        </Button>
      </form>
    </div>
  )
}

