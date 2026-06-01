import React, { useEffect, useRef, useState } from 'react';
import NumberFlow from '@number-flow/react';

export default function AnimatedNumber({ value }) {
  // Карман памяти, чтобы помнить, какая цена была до этого клика
  const [displayValue, setDisplayValue] = useState(value);
  const prevValueRef = useRef(value);

  useEffect(() => {
    // Если значение больше нуля, то обновляется стоимость на экране
    if (value > 0) {
      setDisplayValue(value);
    }

    // Если значение стало 0, то оставляем видимую стоимость такой же
    prevValueRef.current = value;
  }, [value]);

  // Защита от отображения нуля при первом рендере
  if (value === 0 && displayValue === 0) {
    return <span className="text-base font-black text-white leading-6">...</span>;
  }

  // Если корзина опустела, то вместо 0 показываем последнюю стоимость
  const currentPrice = value === 0 ? displayValue : value;

  return (
    <div className="flex h-6 w-20 items-center justify-center overflow-hidden select-none">
      <NumberFlow
        value={currentPrice}
        // Отключаем горизонтальное плавание при переходе с надписи "Корзина"
        animated={prevValueRef.current !== 0}
        springs={{
          layout: { type: 'spring', stiffness: 140, damping: 16, mass: 0.5 },
        }}
        className="text-base font-black text-white leading-6 tracking-tight tabular-nums"
      />
      <span className="ml-1 text-base font-black text-white leading-6">₽</span>
    </div>
  );
}
