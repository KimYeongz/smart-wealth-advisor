"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { formatThaiDate } from "@/lib/utils";
import { Phone, Mail, MessageCircle, Send, Clock, CheckCircle, Calendar } from "lucide-react";

interface Message {
    id: string;
    sender: "user" | "advisor";
    text: string;
    timestamp: Date;
    read: boolean;
}

interface TimeSlot {
    id: string;
    time: string;
    available: boolean;
}

const mockMessages: Message[] = [
    {
        id: "1",
        sender: "advisor",
        text: "สวัสดีครับ มีอะไรให้ช่วยเหลือไหมครับ?",
        timestamp: new Date("2024-01-15T09:00:00"),
        read: true,
    },
    {
        id: "2",
        sender: "user",
        text: "สอบถามเรื่องการลงทุนใน RMF ครับ",
        timestamp: new Date("2024-01-15T09:05:00"),
        read: true,
    },
    {
        id: "3",
        sender: "advisor",
        text: "ได้ครับ RMF เหมาะสำหรับการลงทุนระยะยาวและสามารถลดหย่อนภาษีได้สูงสุด 30% ของรายได้ ไม่เกิน 500,000 บาท อยากทราบรายละเอียดด้านไหนเพิ่มเติมครับ?",
        timestamp: new Date("2024-01-15T09:10:00"),
        read: true,
    },
];

const timeSlots: TimeSlot[] = [
    { id: "1", time: "09:00 - 10:00", available: true },
    { id: "2", time: "10:00 - 11:00", available: false },
    { id: "3", time: "11:00 - 12:00", available: true },
    { id: "4", time: "13:00 - 14:00", available: true },
    { id: "5", time: "14:00 - 15:00", available: false },
    { id: "6", time: "15:00 - 16:00", available: true },
    { id: "7", time: "16:00 - 17:00", available: true },
];

export default function ContactAdvisorPage() {
    const [messages, setMessages] = useState<Message[]>(mockMessages);
    const [newMessage, setNewMessage] = useState("");
    const [activeTab, setActiveTab] = useState<"chat" | "schedule">("chat");
    const [selectedDate, setSelectedDate] = useState<string>("");
    const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
    const [bookingSuccess, setBookingSuccess] = useState(false);

    const handleSendMessage = () => {
        if (!newMessage.trim()) return;

        const userMessage: Message = {
            id: `${Date.now()}`,
            sender: "user",
            text: newMessage,
            timestamp: new Date(),
            read: false,
        };
        setMessages((prev) => [...prev, userMessage]);
        setNewMessage("");

        // Simulate advisor response
        setTimeout(() => {
            const advisorMessage: Message = {
                id: `${Date.now() + 1}`,
                sender: "advisor",
                text: "ขอบคุณสำหรับข้อความครับ ผมจะตอบกลับโดยเร็วที่สุดครับ",
                timestamp: new Date(),
                read: false,
            };
            setMessages((prev) => [...prev, advisorMessage]);
        }, 1500);
    };

    const handleBookAppointment = () => {
        if (!selectedDate || !selectedSlot) return;
        setBookingSuccess(true);
        setTimeout(() => {
            setBookingSuccess(false);
            setSelectedSlot(null);
        }, 3000);
    };

    return (
        <DashboardLayout>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold">
                    <span className="text-gradient">📞 ติดต่อที่ปรึกษา</span>
                </h1>
                <p className="text-gray-500 mt-2">
                    สนทนาหรือนัดหมายกับที่ปรึกษาการเงินของคุณ
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Advisor Info */}
                <div className="glass-card p-6">
                    <div className="text-center mb-6">
                        <div className="w-24 h-24 mx-auto bg-gradient-to-br from-primary to-blue-500 rounded-full flex items-center justify-center text-4xl mb-4">
                            👨‍💼
                        </div>
                        <h3 className="text-xl font-semibold text-white">คุณพิชชาพล ดวิเม</h3>
                        <p className="text-gray-400">ที่ปรึกษาการเงินอาวุโส</p>
                        <div className="flex items-center justify-center gap-2 mt-2">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            <span className="text-sm text-green-400">ออนไลน์</span>
                        </div>
                    </div>

                    <div className="space-y-4 mb-6">
                        <div className="flex items-center gap-3 text-gray-300 p-3 bg-dark-100 rounded-lg">
                            <Phone className="w-5 h-5 text-primary" />
                            <span>082-345-6789</span>
                        </div>
                        <div className="flex items-center gap-3 text-gray-300 p-3 bg-dark-100 rounded-lg">
                            <Mail className="w-5 h-5 text-primary" />
                            <span>advisor@smartwealth.th</span>
                        </div>
                        <div className="flex items-center gap-3 text-gray-300 p-3 bg-dark-100 rounded-lg">
                            <Clock className="w-5 h-5 text-primary" />
                            <span>จ-ศ 09:00 - 17:00 น.</span>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <a href="tel:0823456789">
                            <Button className="w-full">
                                <Phone className="w-4 h-4 mr-2" />
                                โทรหาที่ปรึกษา
                            </Button>
                        </a>
                        <a href="https://line.me" target="_blank" rel="noopener noreferrer">
                            <Button variant="secondary" className="w-full">
                                <MessageCircle className="w-4 h-4 mr-2" />
                                LINE Official
                            </Button>
                        </a>
                    </div>

                    {/* Stats */}
                    <div className="mt-6 pt-6 border-t border-gray-700">
                        <div className="grid grid-cols-2 gap-4 text-center">
                            <div>
                                <p className="text-2xl font-bold text-primary">12+</p>
                                <p className="text-xs text-gray-500">ปีประสบการณ์</p>
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-primary">150+</p>
                                <p className="text-xs text-gray-500">ลูกค้าที่ดูแล</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Chat / Schedule */}
                <div className="lg:col-span-2">
                    {/* Tabs */}
                    <div className="flex border-b border-gray-700 mb-6">
                        <button
                            className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${activeTab === "chat"
                                    ? "text-primary border-b-2 border-primary"
                                    : "text-gray-400 hover:text-white"
                                }`}
                            onClick={() => setActiveTab("chat")}
                        >
                            💬 แชท
                        </button>
                        <button
                            className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${activeTab === "schedule"
                                    ? "text-primary border-b-2 border-primary"
                                    : "text-gray-400 hover:text-white"
                                }`}
                            onClick={() => setActiveTab("schedule")}
                        >
                            📅 นัดหมาย
                        </button>
                    </div>

                    {activeTab === "chat" && (
                        <div className="glass-card p-6">
                            {/* Messages */}
                            <div className="h-96 overflow-y-auto mb-4 space-y-4">
                                {messages.map((msg) => (
                                    <div
                                        key={msg.id}
                                        className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                                    >
                                        <div
                                            className={`max-w-[70%] p-4 rounded-2xl ${msg.sender === "user"
                                                    ? "bg-primary text-white rounded-br-md"
                                                    : "bg-dark-100 text-gray-200 rounded-bl-md"
                                                }`}
                                        >
                                            <p>{msg.text}</p>
                                            <p className={`text-xs mt-2 ${msg.sender === "user" ? "text-primary-200" : "text-gray-500"}`}>
                                                {formatThaiDate(msg.timestamp)}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Input */}
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                                    placeholder="พิมพ์ข้อความ..."
                                    className="flex-1 bg-dark-100 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:border-primary focus:outline-none"
                                />
                                <Button onClick={handleSendMessage} className="px-6">
                                    <Send className="w-5 h-5" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {activeTab === "schedule" && (
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-semibold text-white mb-4">📅 เลือกวันและเวลา</h3>

                            {bookingSuccess ? (
                                <div className="text-center py-12">
                                    <div className="w-20 h-20 mx-auto bg-green-500/20 rounded-full flex items-center justify-center mb-4">
                                        <CheckCircle className="w-10 h-10 text-green-500" />
                                    </div>
                                    <h4 className="text-xl font-semibold text-white mb-2">จองนัดหมายสำเร็จ!</h4>
                                    <p className="text-gray-400">
                                        ที่ปรึกษาจะติดต่อกลับเพื่อยืนยันนัดหมาย
                                    </p>
                                </div>
                            ) : (
                                <>
                                    <div className="mb-6">
                                        <Input
                                            label="เลือกวันที่"
                                            type="date"
                                            value={selectedDate}
                                            onChange={(e) => setSelectedDate(e.target.value)}
                                            min={new Date().toISOString().split("T")[0]}
                                        />
                                    </div>

                                    {selectedDate && (
                                        <>
                                            <p className="text-sm text-gray-400 mb-3">เลือกช่วงเวลา:</p>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                                                {timeSlots.map((slot) => (
                                                    <button
                                                        key={slot.id}
                                                        disabled={!slot.available}
                                                        onClick={() => setSelectedSlot(slot.id)}
                                                        className={`p-3 rounded-lg text-sm font-medium transition-all ${!slot.available
                                                                ? "bg-dark-100 text-gray-600 cursor-not-allowed"
                                                                : selectedSlot === slot.id
                                                                    ? "bg-primary text-white"
                                                                    : "bg-dark-100 text-gray-300 hover:bg-dark-50 border border-gray-700"
                                                            }`}
                                                    >
                                                        {slot.time}
                                                        {!slot.available && (
                                                            <span className="block text-xs text-gray-600">ไม่ว่าง</span>
                                                        )}
                                                    </button>
                                                ))}
                                            </div>

                                            <Button
                                                onClick={handleBookAppointment}
                                                disabled={!selectedSlot}
                                                className="w-full"
                                            >
                                                <Calendar className="w-4 h-4 mr-2" />
                                                ยืนยันนัดหมาย
                                            </Button>
                                        </>
                                    )}
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
