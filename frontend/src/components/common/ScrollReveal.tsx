"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";

export type ScrollRevealAnimation =
  | "fade-up"
  | "fade-down"
  | "fade-left"
  | "fade-right"
  | "zoom-in"
  | "fade";

export interface ScrollRevealProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  animation?: ScrollRevealAnimation;
  delay?: number; // milliseconds
  duration?: number; // milliseconds
  distance?: number; // pixels
  threshold?: number;
  rootMargin?: string;
  once?: boolean;
  as?: React.ElementType;
  className?: string;
}

export function useScrollReveal({
  threshold = 0,
  rootMargin = "150px 0px 50px 0px",
  once = true,
}: {
  threshold?: number;
  rootMargin?: string;
  once?: boolean;
} = {}) {
  const ref = useRef<any>(null);
  const [isRevealed, setIsRevealed] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    // Immediate check: reduced-motion or SSR or print
    if (
      typeof window === "undefined" ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      setIsRevealed(true);
      return;
    }

    // Check if element is already in view or has been scrolled past
    const checkVisible = () => {
      const rect = element.getBoundingClientRect();
      // If top edge is inside viewport or has passed the top, it should be revealed
      if (rect.top < window.innerHeight + 50) {
        setIsRevealed(true);
        return true;
      }
      return false;
    };

    if (checkVisible()) {
      if (once) return;
    }

    if (!("IntersectionObserver" in window)) {
      setIsRevealed(true);
      return;
    }

    let observer: IntersectionObserver | null = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (
            entry.isIntersecting ||
            entry.boundingClientRect.top < window.innerHeight + 50
          ) {
            setIsRevealed(true);
            if (once && observer) {
              observer.unobserve(entry.target);
              observer.disconnect();
              observer = null;
            }
          } else if (!once) {
            setIsRevealed(false);
          }
        });
      },
      { threshold, rootMargin }
    );

    observer.observe(element);

    // Passive scroll listener fallback for fast scrolling or rapid jumps
    const handleScroll = () => {
      if (checkVisible() && once) {
        window.removeEventListener("scroll", handleScroll);
        if (observer) {
          observer.disconnect();
          observer = null;
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (observer) {
        observer.disconnect();
      }
    };
  }, [threshold, rootMargin, once]);

  return { ref, isRevealed };
}

export const ScrollReveal: React.FC<ScrollRevealProps> = ({
  children,
  animation = "fade-up",
  delay = 0,
  duration = 600,
  distance = 28,
  threshold = 0,
  rootMargin = "150px 0px 50px 0px",
  once = true,
  as: Component = "div",
  className = "",
  style,
  ...rest
}) => {
  const { ref, isRevealed } = useScrollReveal({ threshold, rootMargin, once });

  const customStyle: React.CSSProperties = {
    ...style,
    ...(delay > 0 ? { "--reveal-delay": `${delay}ms` } : {}),
    ...(duration !== 600 ? { "--reveal-duration": `${duration}ms` } : {}),
    ...(distance !== 28 ? { "--reveal-distance": `${distance}px` } : {}),
  } as React.CSSProperties;

  const animationClass = `reveal-${animation}`;

  return (
    <Component
      ref={ref}
      className={`scroll-reveal ${animationClass} ${isRevealed ? "is-revealed" : ""} ${className}`.trim()}
      style={customStyle}
      {...rest}
    >
      {children}
    </Component>
  );
};

export interface ScrollRevealGroupProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  animation?: ScrollRevealAnimation;
  staggerInterval?: number; // ms between items
  baseDelay?: number;
  duration?: number;
  distance?: number;
  threshold?: number;
  rootMargin?: string;
  as?: React.ElementType;
  className?: string;
  itemClassName?: string;
}

export const ScrollRevealGroup: React.FC<ScrollRevealGroupProps> = ({
  children,
  animation = "fade-up",
  staggerInterval = 80,
  baseDelay = 0,
  duration = 600,
  distance = 28,
  threshold = 0,
  rootMargin = "150px 0px 50px 0px",
  as: Component = "div",
  className = "",
  itemClassName = "",
  ...rest
}) => {
  return (
    <Component className={className} {...rest}>
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child;
        return (
          <ScrollReveal
            animation={animation}
            delay={baseDelay + index * staggerInterval}
            duration={duration}
            distance={distance}
            threshold={threshold}
            rootMargin={rootMargin}
            className={itemClassName}
          >
            {child}
          </ScrollReveal>
        );
      })}
    </Component>
  );
};

export default ScrollReveal;
